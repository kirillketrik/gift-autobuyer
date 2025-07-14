class AutobuyerError(Exception):
    def __init__(self, message: str):
        self.message: str = message


class OldGiftsReceivedError(AutobuyerError):
    def __init__(self):
        super().__init__('There are no new gifts since last update')


class GiftSoldOutError(AutobuyerError):
    def __init__(self):
        super().__init__('The gift was sold out')
