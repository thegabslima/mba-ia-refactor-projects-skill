import hmac
from functools import wraps

from flask import request

from config.settings import Settings
from models.errors import AppError


def require_admin(view):
    """Exige o header X-Admin-Token igual ao ADMIN_TOKEN; sem token configurado a rota fica desativada."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        enviado = request.headers.get("X-Admin-Token", "")
        if not Settings.ADMIN_TOKEN or not hmac.compare_digest(enviado, Settings.ADMIN_TOKEN):
            raise AppError("Acesso negado", 403)
        return view(*args, **kwargs)

    return wrapper
