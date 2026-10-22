from flask import jsonify

from config.settings import Settings
from models.admin_model import AdminModel
from models.database import get_db


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": Settings.VERSAO,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": AdminModel(get_db()).contagens(),
        "versao": Settings.VERSAO,
        "ambiente": Settings.ENVIRONMENT,
    }), 200
