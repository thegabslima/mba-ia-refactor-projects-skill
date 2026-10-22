from flask import jsonify, request

from database import commit_or_raise, db
from models.category import Category
from models.task import Task
from utils.errors import AppError
from utils.validators import validate_category_payload


def _get_category_or_404(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        raise AppError('Categoria não encontrada', 404)
    return category


def get_categories():
    counts = Task.count_by_category()
    result = []
    for category in Category.list_all():
        data = category.to_dict()
        data['task_count'] = counts.get(category.id, 0)
        result.append(data)
    return jsonify(result), 200


def create_category():
    fields = validate_category_payload(request.get_json(silent=True))
    category = Category(**fields)
    db.session.add(category)
    commit_or_raise('Erro ao criar categoria')
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = _get_category_or_404(cat_id)
    for name, value in validate_category_payload(request.get_json(silent=True), partial=True).items():
        setattr(category, name, value)
    commit_or_raise('Erro ao atualizar')
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category = _get_category_or_404(cat_id)
    db.session.delete(category)
    commit_or_raise('Erro ao deletar')
    return jsonify({'message': 'Categoria deletada'}), 200
