from tortoise import Model, fields


class GiftFilterModel(Model):
    class Meta:
        table = 'gift_filters'

    id = fields.IntField(pk=True)
    """ID фильтра"""
    enabled = fields.BooleanField(default=True)
    """Включен ли фильтр"""
    min_supply = fields.IntField(default=-1)
    """Минимальный саплай подарков. Если значение равняется -1 значит данная опция выключена"""
    max_supply = fields.IntField(default=-1)
    """Максимальный саплай подарка. Если значение равняется -1 значит данная опция выключена"""
    min_price = fields.IntField(default=-1)
    """Минимальная цена подарка. Если значение равняется -1 значит данная опция выключена"""
    max_price = fields.IntField(default=-1)
    """Максимальная цена подарка. Если значение равняется -1 значит данная опция выключена"""
    priority = fields.IntField(default=0)
    """Приоритет покупки подарков"""
    weight = fields.IntField(default=-1)
    """
    Часть бюджета, которые выделяется на подарки, попавшие под данный фильтр.
    Если значение равняется -1 значит данная опция выключена
    """
    max_buy_count = fields.IntField(default=-1)
    """Максимальное кол-во подарков, которое может быть куплено"""
    max_spend_money = fields.IntField(default=-1)
    """Максимальная сумма, которая может быть потрачена на подарки, попавшие под данный фильтр"""
