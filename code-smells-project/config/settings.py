import os
import secrets


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    ENVIRONMENT = os.environ.get("APP_ENV", "desenvolvimento")
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 5000))
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
    VERSAO = "1.0.0"

    CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
    STATUS_PEDIDO = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
    NOME_MIN = 2
    NOME_MAX = 200

    # (faturamento acima de, percentual de desconto), do maior para o menor
    DESCONTO_FAIXAS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))
