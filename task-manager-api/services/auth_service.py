from itsdangerous import BadSignature, URLSafeTimedSerializer

from config.settings import Settings


def _serializer():
    return URLSafeTimedSerializer(Settings.SECRET_KEY, salt='task-manager-auth')


def issue_token(user):
    return _serializer().dumps({'user_id': user.id})


def read_token(token):
    """Retorna o user_id do token ou None se inválido/expirado."""
    try:
        return _serializer().loads(token, max_age=Settings.TOKEN_MAX_AGE_SECONDS)['user_id']
    except BadSignature:
        return None
