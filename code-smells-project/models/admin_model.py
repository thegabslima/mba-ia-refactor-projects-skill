from models.errors import AppError

TABELAS_RESET = ("itens_pedido", "pedidos", "produtos", "usuarios")


class AdminModel:
    def __init__(self, db):
        self.db = db

    def resetar(self):
        for tabela in TABELAS_RESET:
            self.db.execute(f"DELETE FROM {tabela}")
        self.db.commit()

    def consultar(self, sql):
        """Executa somente um único SELECT."""
        comando = sql.strip().rstrip(";").strip()
        if not comando.upper().startswith("SELECT") or ";" in comando:
            raise AppError("Apenas um comando SELECT é permitido")
        try:
            rows = self.db.execute(comando).fetchall()
        except Exception as exc:
            raise AppError(f"Query inválida: {exc}")
        return [dict(row) for row in rows]

    def contagens(self):
        """Contagem de registros usada pelo health check."""
        return {
            tabela: self.db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            for tabela in ("produtos", "usuarios", "pedidos")
        }
