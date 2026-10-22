from flask import jsonify

from models.database import get_db
from models.relatorio_model import RelatorioModel


def relatorio_vendas():
    return jsonify({"dados": RelatorioModel(get_db()).vendas(), "sucesso": True}), 200
