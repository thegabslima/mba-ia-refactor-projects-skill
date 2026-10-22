import logging

from flask import jsonify, request

from database import commit_or_raise, db
from models.category import Category
from models.task import Task
from models.user import User
from utils.errors import AppError
from utils.helpers import utcnow
from utils.validators import validate_task_payload

logger = logging.getLogger(__name__)


def _get_task_or_404(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise AppError('Task não encontrada', 404)
    return task


def _ensure_references(fields):
    if fields.get('user_id') and not db.session.get(User, fields['user_id']):
        raise AppError('Usuário não encontrado', 404)
    if fields.get('category_id') and not db.session.get(Category, fields['category_id']):
        raise AppError('Categoria não encontrada', 404)


def _optional_int(name):
    raw = request.args.get(name, '')
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise AppError(f'Parâmetro {name} inválido')


def get_tasks():
    result = []
    for task in Task.list_with_relations():
        data = task.to_dict(include_overdue=True)
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        result.append(data)
    return jsonify(result), 200


def get_task(task_id):
    return jsonify(_get_task_or_404(task_id).to_dict(include_overdue=True)), 200


def create_task():
    fields = validate_task_payload(request.get_json(silent=True))
    _ensure_references(fields)

    task = Task(**fields)
    db.session.add(task)
    commit_or_raise('Erro ao criar task')
    logger.info('Task criada: %s - %s', task.id, task.title)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = _get_task_or_404(task_id)
    fields = validate_task_payload(request.get_json(silent=True), partial=True)
    _ensure_references(fields)

    for name, value in fields.items():
        setattr(task, name, value)
    task.updated_at = utcnow()
    commit_or_raise('Erro ao atualizar')
    logger.info('Task atualizada: %s', task.id)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    db.session.delete(task)
    commit_or_raise('Erro ao deletar')
    logger.info('Task deletada: %s', task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    tasks = Task.search(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=_optional_int('priority'),
        user_id=_optional_int('user_id'),
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    total = Task.total()
    by_status = Task.count_by_status()
    done = by_status.get('done', 0)
    return jsonify({
        'total': total,
        'pending': by_status.get('pending', 0),
        'in_progress': by_status.get('in_progress', 0),
        'done': done,
        'cancelled': by_status.get('cancelled', 0),
        'overdue': len(Task.overdue()),
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }), 200
