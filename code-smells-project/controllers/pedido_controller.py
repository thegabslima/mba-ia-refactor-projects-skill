from flask import jsonify, request

from config.settings import Settings
from models.database import get_db
from models.errors import AppError
from models.pedido_model import PedidoModel
from services import notificacao_service


def _parse_itens(itens):
    if not isinstance(itens, list) or not itens:
        raise AppError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        if not isinstance(item, dict):
            raise AppError("Item de pedido inválido")
        for campo in ("produto_id", "quantidade"):
            valor = item.get(campo)
            if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
                raise AppError(f"Item inválido: {campo} deve ser inteiro positivo")
    return itens


def criar_pedido():
    dados = request.get_json(silent=True)
    if not dados or not isinstance(dados, dict):
        raise AppError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    if not usuario_id:
        raise AppError("Usuario ID é obrigatório")
    itens = _parse_itens(dados.get("itens", []))

    resultado = PedidoModel(get_db()).criar(usuario_id, itens)
    notificacao_service.pedido_criado(resultado["pedido_id"], usuario_id)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": PedidoModel(get_db()).listar_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": PedidoModel(get_db()).listar_todos(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True)
    novo_status = dados.get("status", "") if isinstance(dados, dict) else ""
    if novo_status not in Settings.STATUS_PEDIDO:
        raise AppError("Status inválido")

    PedidoModel(get_db()).atualizar_status(pedido_id, novo_status)
    notificacao_service.status_alterado(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
