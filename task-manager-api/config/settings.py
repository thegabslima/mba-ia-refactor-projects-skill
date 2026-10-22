import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 5000))

    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

    TOKEN_MAX_AGE_SECONDS = 3600

    VALID_STATUSES = ("pending", "in_progress", "done", "cancelled")
    CLOSED_STATUSES = ("done", "cancelled")
    VALID_ROLES = ("user", "admin", "manager")
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5
    DEFAULT_PRIORITY = 3
    HIGH_PRIORITY_MAX = 2
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_PASSWORD_LENGTH = 4
    DEFAULT_COLOR = "#000000"
    RECENT_DAYS = 7
