from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from utils.errors import AppError

db = SQLAlchemy()


def commit_or_raise(message):
    """Faz commit; em caso de erro faz rollback e levanta AppError 500 com a mensagem dada."""
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise AppError(message, 500)
