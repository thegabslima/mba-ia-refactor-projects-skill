class AppError(Exception):
    """Erro de negócio/validação; o handler central converte em resposta JSON."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
