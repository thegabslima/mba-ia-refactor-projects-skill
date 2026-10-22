class AppError(Exception):
    """Erro de validação/negócio; o handler central converte em JSON {'error': ...}."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
