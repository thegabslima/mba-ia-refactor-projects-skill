from werkzeug.security import check_password_hash, generate_password_hash

COLUNAS_PUBLICAS = "id, nome, email, tipo, criado_em"


class UsuarioModel:
    def __init__(self, db):
        self.db = db

    def listar(self):
        rows = self.db.execute(f"SELECT {COLUNAS_PUBLICAS} FROM usuarios").fetchall()
        return [dict(row) for row in rows]

    def buscar_por_id(self, usuario_id):
        row = self.db.execute(
            f"SELECT {COLUNAS_PUBLICAS} FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return dict(row) if row else None

    def autenticar(self, email, senha):
        row = self.db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        if row is None or not check_password_hash(row["senha"], senha):
            return None
        return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}

    def criar(self, nome, email, senha, tipo="cliente"):
        cursor = self.db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha), tipo),
        )
        self.db.commit()
        return cursor.lastrowid
