class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def listar(self):
        rows = self.db.execute("SELECT * FROM produtos").fetchall()
        return [dict(row) for row in rows]

    def buscar_por_id(self, produto_id):
        row = self.db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        return dict(row) if row else None

    def criar(self, nome, descricao, preco, estoque, categoria):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        self.db.commit()
        return cursor.lastrowid

    def atualizar(self, produto_id, nome, descricao, preco, estoque, categoria):
        self.db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        self.db.commit()

    def deletar(self, produto_id):
        self.db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self.db.commit()

    def buscar(self, termo, categoria=None, preco_min=None, preco_max=None):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            params += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)
        return [dict(row) for row in self.db.execute(query, params).fetchall()]
