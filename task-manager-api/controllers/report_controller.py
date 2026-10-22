from flask import jsonify

from database import db
from models.user import User
from services import report_service
from utils.errors import AppError


def summary_report():
    return jsonify(report_service.summary()), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)
    return jsonify(report_service.user_report(user)), 200
