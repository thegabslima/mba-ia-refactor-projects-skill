import logging
import sqlite3

from flask import jsonify

from models.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status

    @app.errorhandler(sqlite3.IntegrityError)
    def handle_integrity_error(error):
        logger.warning("Violação de integridade: %s", error)
        return jsonify({"erro": "Operação viola uma restrição de integridade", "sucesso": False}), 409

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        code = getattr(error, "code", None)
        if isinstance(code, int):  # HTTPException (404, 405, 415...)
            return jsonify({"erro": getattr(error, "description", "Erro"), "sucesso": False}), code
        logger.exception("Erro não tratado: %s", error)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
