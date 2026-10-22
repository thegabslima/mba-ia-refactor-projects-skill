from datetime import datetime

from config.settings import Settings
from utils.errors import AppError
from utils.helpers import validate_email


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _parse_tags(tags):
    if isinstance(tags, list):
        return ','.join(str(tag) for tag in tags)
    return tags


def validate_task_payload(data, partial=False):
    """Valida o corpo de criação (partial=False) ou atualização (partial=True) de task."""
    if not data or not isinstance(data, dict):
        raise AppError('Dados inválidos')

    fields = {}

    if not partial or 'title' in data:
        title = data.get('title')
        if not partial and not title:
            raise AppError('Título é obrigatório')
        if not isinstance(title, str):
            raise AppError('Título inválido')
        if len(title) < Settings.MIN_TITLE_LENGTH:
            raise AppError('Título muito curto')
        if len(title) > Settings.MAX_TITLE_LENGTH:
            raise AppError('Título muito longo')
        fields['title'] = title

    if not partial or 'description' in data:
        fields['description'] = data.get('description', '')

    if not partial or 'status' in data:
        status = data.get('status', 'pending')
        if status not in Settings.VALID_STATUSES:
            raise AppError('Status inválido')
        fields['status'] = status

    if not partial or 'priority' in data:
        priority = data.get('priority', Settings.DEFAULT_PRIORITY)
        if not _is_int(priority) or not Settings.MIN_PRIORITY <= priority <= Settings.MAX_PRIORITY:
            raise AppError('Prioridade deve ser entre 1 e 5')
        fields['priority'] = priority

    if not partial or 'user_id' in data:
        fields['user_id'] = data.get('user_id')
    if not partial or 'category_id' in data:
        fields['category_id'] = data.get('category_id')

    if 'due_date' in data and data['due_date']:
        try:
            fields['due_date'] = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except (ValueError, TypeError):
            raise AppError('Formato de data inválido. Use YYYY-MM-DD')
    elif 'due_date' in data:
        fields['due_date'] = None

    if 'tags' in data and (partial or data['tags']):
        fields['tags'] = _parse_tags(data['tags'])

    return fields


def validate_user_payload(data, partial=False):
    if not data or not isinstance(data, dict):
        raise AppError('Dados inválidos')

    fields = {}

    if not partial:
        if not data.get('name'):
            raise AppError('Nome é obrigatório')
        if not data.get('email'):
            raise AppError('Email é obrigatório')
        if not data.get('password'):
            raise AppError('Senha é obrigatória')

    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name']:
            raise AppError('Nome inválido')
        fields['name'] = data['name']

    if 'email' in data:
        if not validate_email(data['email']):
            raise AppError('Email inválido')
        fields['email'] = data['email']

    if 'password' in data:
        password = data['password']
        if not isinstance(password, str) or len(password) < Settings.MIN_PASSWORD_LENGTH:
            raise AppError(
                f'Senha deve ter no mínimo {Settings.MIN_PASSWORD_LENGTH} caracteres' if not partial
                else 'Senha muito curta'
            )
        fields['password'] = password

    if not partial or 'role' in data:
        role = data.get('role', 'user')
        if role not in Settings.VALID_ROLES:
            raise AppError('Role inválido')
        fields['role'] = role

    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise AppError('Campo active deve ser booleano')
        fields['active'] = data['active']

    return fields


def validate_category_payload(data, partial=False):
    if not data or not isinstance(data, dict):
        raise AppError('Dados inválidos')

    fields = {}
    if not partial and not data.get('name'):
        raise AppError('Nome é obrigatório')
    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name']:
            raise AppError('Nome inválido')
        fields['name'] = data['name']
    if not partial or 'description' in data:
        fields['description'] = data.get('description', '')
    if not partial or 'color' in data:
        fields['color'] = data.get('color', Settings.DEFAULT_COLOR)
    return fields
