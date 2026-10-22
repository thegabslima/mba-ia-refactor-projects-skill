import logging

from flask import jsonify, request

from models.admin_model import AdminModel
from models.database import get_db
from models.errors import AppError

logger = logging.getLogger(__name__)


def reset_database():
    AdminModel(get_db()).resetar()
    logger.warning("Banco de dados resetado via /admin/reset-db")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    dados = request.get_json(silent=True)
    sql = dados.get("sql", "") if isinstance(dados, dict) else ""
    if not sql:
        raise AppError("Query não informada")
    return jsonify({"dados": AdminModel(get_db()).consultar(sql), "sucesso": True}), 200
