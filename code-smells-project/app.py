import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from middlewares.error_handler import register_error_handlers
from models.database import close_db, init_db
from views.routes import api

logger = logging.getLogger(__name__)


def create_app():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = Settings.SECRET_KEY
    CORS(app)

    init_db()
    app.teardown_appcontext(close_db)
    app.register_blueprint(api)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    logger.info("Servidor em http://%s:%s (debug=%s)", Settings.HOST, Settings.PORT, Settings.DEBUG)
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
