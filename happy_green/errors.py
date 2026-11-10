class HappyGreenError(Exception):
    """Erro que pode ser apresentado ao usuário sem detalhes internos."""


class ValidationError(HappyGreenError):
    pass


class NotFoundError(HappyGreenError):
    pass


class ConflictError(HappyGreenError):
    pass


class PersistenceError(HappyGreenError):
    pass


class ConfigurationError(HappyGreenError):
    pass
