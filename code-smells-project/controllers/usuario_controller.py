import logging

from flask import jsonify, request

from models.database import get_db
from models.errors import AppError
from models.usuario_model import UsuarioModel

logger = logging.getLogger(__name__)


def listar_usuarios():
    return jsonify({"dados": UsuarioModel(get_db()).listar(), "sucesso": True}), 200


def buscar_usuario(id):
    usuario = UsuarioModel(get_db()).buscar_por_id(id)
    if not usuario:
        raise AppError("Usuário não encontrado", 404)
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados or not isinstance(dados, dict):
        raise AppError("Dados inválidos")

    nome, email, senha = dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")
    if not nome or not email or not senha:
        raise AppError("Nome, email e senha são obrigatórios")
    if not all(isinstance(v, str) for v in (nome, email, senha)):
        raise AppError("Nome, email e senha devem ser texto")

    usuario_id = UsuarioModel(get_db()).criar(nome, email, senha)
    logger.info("Usuário criado: %s", email)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = request.get_json(silent=True)
    if not dados or not isinstance(dados, dict):
        raise AppError("Dados inválidos")

    email, senha = dados.get("email", ""), dados.get("senha", "")
    if not email or not senha:
        raise AppError("Email e senha são obrigatórios")

    usuario = UsuarioModel(get_db()).autenticar(str(email), str(senha))
    if not usuario:
        logger.info("Login falhou: %s", email)
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
    logger.info("Login bem-sucedido: %s", email)
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
