from tortoise import Model, fields


class ReceiverModel(Model):
    class Meta:
        table = 'receivers'

    id = fields.IntField(pk=True)
    """ID пользователя/канала, которому будет отправляться купленный подарок"""
    username = fields.CharField(max_length=32)
    """Тег пользователя/канала, которому будет отправляться купленный подарок"""
