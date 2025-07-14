from pydantic import BaseModel, Field

from .gift import Gift
from .gift_filter import GiftFilter


class GiftAllocation(BaseModel):
    filter: GiftFilter
    gift: Gift
    buy_amount: int = Field(..., description='Кол-во подарков, которое надо будет купить')


class GiftAllocationRule(BaseModel):
    min_supply: int = -1
    """
    Минимальное значение тиража (supply), с которого начинаются подарки, попадающие под данное правило.
    Например, min_supply=0 включает в выборку самые редкие подарки.
    """

    max_supply: int = -1
    """
    Максимальное значение тиража (supply), до которого включительно действует правило.
    Например, max_supply=1000 означает, что подарки с supply ≤ 1000 будут включены.
    """

    min_price: int = -1
    """
    Минимальная цена подарков, которые разрешены для покупки по данному правилу.
    Если равно 0, нижняя граница цены не применяется.
    """

    max_price: int = -1
    """
    Максимальная цена подарков, которые разрешены для покупки по данному правилу.
    Если равно 0, верхняя граница цены не применяется.
    """

    weight: int = 0
    """
    Весовой коэффициент — используется при стратегии пропорционального распределения бюджета.
    Чем выше значение, тем большая доля общего бюджета выделяется на эту категорию.
    Может быть 0, если используется `priority`.
    """

    priority: int = 0
    """
    Приоритет правила.
    Если > 0, правило будет обработано раньше других в порядке убывания приоритета, и все подходящие подарки будут покупаться,
    пока хватает средств (игнорируется `weight`).
    Если равно 0, правило участвует только в весовом распределении.
    """

    max_count: int = -1
    """
    Максимальное количество подарков, которые можно купить по данному правилу.
    Применяется **только если используется приоритет** (`priority > 0`).
    Если установлено значение > 0, ограничивает количество покупок, даже если хватает бюджета.
    Если значение -1 (по умолчанию), количество не ограничено.
    """

    exclude: bool = False
    """
    Исключить правило из обработки.
    Если True — ни одна фильтрация и стратегия покупки не будут применяться.
    Удобно для временного отключения правила без удаления.
    """

    @classmethod
    def validate_rule(cls, rule: "GiftAllocationRule") -> None:
        """
        Проверка бизнес-логики правила:
        🔹 1. Должны быть указаны критерии фильтрации: по supply, по цене или их комбинация.
        🔹 2. Должна быть выбрана хотя бы одна стратегия распределения: либо `priority`, либо `weight > 0`.
        """

        if rule.exclude:
            return  # Правило исключено — не валидируем дальше

        if not (rule.has_supply_filter or rule.has_price_filter):
            raise ValueError(
                "Правило должно содержать хотя бы один фильтр: по supply или по цене "
                "(min_supply/max_supply или min_price/max_price)"
            )

        if rule.weight <= 0 and rule.priority <= 0:
            raise ValueError(
                "Правило должно использовать хотя бы одну стратегию: "
                "либо приоритет (priority > 0), либо весовое распределение (weight > 0)"
            )

    @property
    def has_supply_filter(self) -> bool:
        return self.min_supply >= 0 and self.max_supply >= 0

    @property
    def has_price_filter(self) -> bool:
        return self.min_price >= 0 and self.max_price >= 0

    def match(self, gift: Gift) -> bool:
        """
        Проверяет, удовлетворяет ли подарок условиям правила:
        учитываются только явно заданные границы (>= 0).
        """
        if not gift.supply or not gift.price:
            return True
        if gift.supply < self.min_supply >= 0:
            return False
        if 0 <= self.max_supply < gift.supply:
            return False
        if gift.price < self.min_price >= 0:
            return False
        if 0 <= self.max_price < gift.price:
            return False
        return True

    def __eq__(self, other: "GiftAllocationRule") -> bool:
        if not isinstance(other, GiftAllocationRule):
            return False
        return (
            self.min_supply, self.max_supply, self.min_price, self.max_price
        ) == (
            other.min_supply, other.max_supply, other.min_price, other.max_price
        )

    def __str__(self):
        if self.exclude:
            return "Rule is excluded from allocation."

        parts = []

        # Supply filter
        if self.has_supply_filter:
            parts.append(f"Supply between {self.min_supply} and {self.max_supply}")
        elif self.min_supply >= 0:
            parts.append(f"Supply ≥ {self.min_supply}")
        elif self.max_supply >= 0:
            parts.append(f"Supply ≤ {self.max_supply}")

        # Price filter
        if self.has_price_filter:
            parts.append(f"Price between {self.min_price} and {self.max_price}")
        elif self.min_price >= 0:
            parts.append(f"Price ≥ {self.min_price}")
        elif self.max_price >= 0:
            parts.append(f"Price ≤ {self.max_price}")

        # Strategy
        if self.priority > 0:
            strategy = f"Priority {self.priority}"
            if self.max_count > 0:
                strategy += f", max {self.max_count} items"
            parts.append(strategy)
        elif self.weight > 0:
            parts.append(f"Weight {self.weight}")

        return "; ".join(parts) if parts else "No active filters or strategy defined."
