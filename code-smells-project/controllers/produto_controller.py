import logging

from flask import jsonify, request

from config.settings import Settings
from models.database import get_db
from models.errors import AppError
from models.produto_model import ProdutoModel

logger = logging.getLogger(__name__)


def _parse_produto(dados):
    if not dados or not isinstance(dados, dict):
        raise AppError("Dados inválidos")
    for campo, rotulo in (("nome", "Nome"), ("preco", "Preço"), ("estoque", "Estoque")):
        if campo not in dados:
            raise AppError(f"{rotulo} é obrigatório")

    nome, preco, estoque = dados["nome"], dados["preco"], dados["estoque"]
    categoria = dados.get("categoria", "geral")
    if not isinstance(nome, str):
        raise AppError("Nome inválido")
    if isinstance(preco, bool) or not isinstance(preco, (int, float)):
        raise AppError("Preço inválido")
    if isinstance(estoque, bool) or not isinstance(estoque, int):
        raise AppError("Estoque inválido")
    if preco < 0:
        raise AppError("Preço não pode ser negativo")
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo")
    if len(nome) < Settings.NOME_MIN:
        raise AppError("Nome muito curto")
    if len(nome) > Settings.NOME_MAX:
        raise AppError("Nome muito longo")
    if categoria not in Settings.CATEGORIAS_VALIDAS:
        raise AppError("Categoria inválida. Válidas: " + str(Settings.CATEGORIAS_VALIDAS))
    return nome, dados.get("descricao", ""), preco, estoque, categoria


def _buscar_ou_404(produtos, produto_id):
    produto = produtos.buscar_por_id(produto_id)
    if not produto:
        raise AppError("Produto não encontrado", 404)
    return produto


def listar_produtos():
    produtos = ProdutoModel(get_db()).listar()
    logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = _buscar_ou_404(ProdutoModel(get_db()), id)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    campos = _parse_produto(request.get_json(silent=True))
    produto_id = ProdutoModel(get_db()).criar(*campos)
    logger.info("Produto criado com ID: %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    produtos = ProdutoModel(get_db())
    _buscar_ou_404(produtos, id)
    produtos.atualizar(id, *_parse_produto(request.get_json(silent=True)))
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    produtos = ProdutoModel(get_db())
    _buscar_ou_404(produtos, id)
    produtos.deletar(id)
    logger.info("Produto %s deletado", id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    try:
        preco_min = request.args.get("preco_min")
        preco_max = request.args.get("preco_max")
        preco_min = float(preco_min) if preco_min else None
        preco_max = float(preco_max) if preco_max else None
    except ValueError:
        raise AppError("preco_min e preco_max devem ser numéricos")

    resultados = ProdutoModel(get_db()).buscar(
        request.args.get("q", ""), request.args.get("categoria"), preco_min, preco_max
    )
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
