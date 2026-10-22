import logging

from flask import jsonify

from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        code = getattr(error, 'code', None)
        if isinstance(code, int):  # HTTPException (404, 405, ...)
            return jsonify({'error': getattr(error, 'description', 'Erro')}), code
        logger.exception('Erro não tratado: %s', error)
        return jsonify({'error': 'Erro interno'}), 500
