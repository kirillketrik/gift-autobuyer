class BaseAutobuyerError(Exception):
    pass


class NotAuthorizedError(BaseAutobuyerError):
    pass


class FloodError(BaseAutobuyerError):
    def __init__(self, pause: float):
        self.pause = pause


class BaseGiftProviderError(BaseAutobuyerError):
    pass


class InsufficientBalanceError(BaseAutobuyerError):
    pass


class GiftSoldOutError(BaseGiftProviderError):
    pass
