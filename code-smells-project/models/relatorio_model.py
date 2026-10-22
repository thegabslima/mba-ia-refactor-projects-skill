from config.settings import Settings


def calcular_desconto(faturamento):
    for limite, taxa in Settings.DESCONTO_FAIXAS:
        if faturamento > limite:
            return faturamento * taxa
    return 0


class RelatorioModel:
    def __init__(self, db):
        self.db = db

    def vendas(self):
        row = self.db.execute(
            """
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(total), 0) AS faturamento,
                   COALESCE(SUM(status = 'pendente'), 0) AS pendentes,
                   COALESCE(SUM(status = 'aprovado'), 0) AS aprovados,
                   COALESCE(SUM(status = 'cancelado'), 0) AS cancelados
            FROM pedidos
            """
        ).fetchone()
        total_pedidos = row["total"]
        faturamento = row["faturamento"]
        desconto = calcular_desconto(faturamento)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": row["pendentes"],
            "pedidos_aprovados": row["aprovados"],
            "pedidos_cancelados": row["cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
