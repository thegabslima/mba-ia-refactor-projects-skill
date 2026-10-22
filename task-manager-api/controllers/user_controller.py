import logging

from flask import jsonify, request

from database import commit_or_raise, db
from models.task import Task
from models.user import User
from services import auth_service
from utils.errors import AppError
from utils.validators import validate_user_payload

logger = logging.getLogger(__name__)


def _get_user_or_404(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)
    return user


def _ensure_email_free(email, current_user_id=None):
    existing = User.find_by_email(email)
    if existing and existing.id != current_user_id:
        raise AppError('Email já cadastrado', 409)


def get_users():
    counts = Task.count_by_user()
    result = []
    for user in User.list_all():
        data = user.to_dict()
        data['task_count'] = counts.get(user.id, (0, 0))[0]
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = _get_user_or_404(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.for_user(user_id)]
    return jsonify(data), 200


def create_user():
    fields = validate_user_payload(request.get_json(silent=True))
    _ensure_email_free(fields['email'])

    user = User(name=fields['name'], email=fields['email'], role=fields['role'])
    user.set_password(fields['password'])
    db.session.add(user)
    commit_or_raise('Erro ao criar usuário')
    logger.info('Usuário criado: %s - %s', user.id, user.name)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = _get_user_or_404(user_id)
    fields = validate_user_payload(request.get_json(silent=True), partial=True)
    if 'email' in fields:
        _ensure_email_free(fields['email'], user_id)

    password = fields.pop('password', None)
    for name, value in fields.items():
        setattr(user, name, value)
    if password:
        user.set_password(password)
    commit_or_raise('Erro ao atualizar')
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    db.session.delete(user)  # as tasks do usuário saem junto (cascade no model)
    commit_or_raise('Erro ao deletar')
    logger.info('Usuário deletado: %s', user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    return jsonify([task.to_summary_dict() for task in Task.for_user(user_id)]), 200


def login():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        raise AppError('Dados inválidos')

    email, password = data.get('email'), data.get('password')
    if not email or not password:
        raise AppError('Email e senha são obrigatórios')

    user = User.find_by_email(email) if isinstance(email, str) else None
    if not user or not isinstance(password, str) or not user.check_password(password):
        raise AppError('Credenciais inválidas', 401)
    if not user.active:
        raise AppError('Usuário inativo', 403)

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': auth_service.issue_token(user),
    }), 200
