from models.errors import AppError


class PedidoModel:
    def __init__(self, db):
        self.db = db

    def criar(self, usuario_id, itens):
        """Cria pedido, itens e baixa de estoque em uma única transação."""
        try:
            if self.db.execute("SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)).fetchone() is None:
                raise AppError(f"Usuário {usuario_id} não encontrado")

            total = 0
            produtos = []
            for item in itens:
                produto = self.db.execute(
                    "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (item["produto_id"],)
                ).fetchone()
                if produto is None:
                    raise AppError(f"Produto {item['produto_id']} não encontrado")
                if produto["estoque"] < item["quantidade"]:
                    raise AppError(f"Estoque insuficiente para {produto['nome']}")
                total += produto["preco"] * item["quantidade"]
                produtos.append(produto)

            cursor = self.db.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                (usuario_id, total),
            )
            pedido_id = cursor.lastrowid

            for item, produto in zip(itens, produtos):
                self.db.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                    (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
                )
                self.db.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                    (item["quantidade"], item["produto_id"]),
                )
            self.db.commit()
            return {"pedido_id": pedido_id, "total": total}
        except Exception:
            self.db.rollback()
            raise

    def listar_por_usuario(self, usuario_id):
        rows = self.db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
        return self._com_itens([dict(row) for row in rows])

    def listar_todos(self):
        rows = self.db.execute("SELECT * FROM pedidos").fetchall()
        return self._com_itens([dict(row) for row in rows])

    def atualizar_status(self, pedido_id, novo_status):
        self.db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        self.db.commit()

    def _com_itens(self, pedidos):
        """Anexa os itens de todos os pedidos com uma única query (sem N+1)."""
        for pedido in pedidos:
            pedido["itens"] = []
        if not pedidos:
            return pedidos

        por_id = {pedido["id"]: pedido for pedido in pedidos}
        marcadores = ",".join("?" * len(por_id))
        itens = self.db.execute(
            f"""
            SELECT i.pedido_id, i.produto_id, COALESCE(p.nome, 'Desconhecido') AS produto_nome,
                   i.quantidade, i.preco_unitario
            FROM itens_pedido i
            LEFT JOIN produtos p ON p.id = i.produto_id
            WHERE i.pedido_id IN ({marcadores})
            ORDER BY i.id
            """,
            list(por_id),
        ).fetchall()
        for item in itens:
            por_id[item["pedido_id"]]["itens"].append(
                {
                    "produto_id": item["produto_id"],
                    "produto_nome": item["produto_nome"],
                    "quantidade": item["quantidade"],
                    "preco_unitario": item["preco_unitario"],
                }
            )
        return pedidos
