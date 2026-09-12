"""Recipe ingredient model."""

from dataclasses import dataclass
from decimal import Decimal
from .item import Item


@dataclass
class Ingredient:
    """A quantity of an item, or of any item carrying a given tag, consumed by a recipe."""

    item_name_id: str
    quantity: Decimal
    reducible: bool = False
    tag: bool = False

    def to_readable_string(self) -> str:
        """Format this ingredient as a short human-readable line, e.g. '2 Wood (R)'."""
        reduce = " (R)" if self.reducible else ""
        tag_str = " (T)" if self.tag else ""
        return f"{self.quantity} {self.item_name_id}{reduce}{tag_str}"

    def __eq__(self, other):
        if not isinstance(other, Ingredient):
            return False
        return (self.reducible == other.reducible and
                Item.name_ids_match(self.item_name_id, other.item_name_id) and
                self.quantity == other.quantity)

    def __hash__(self):
        return hash((self.item_name_id, self.quantity, self.reducible))

    def to_dict(self):
        """Serialize this ingredient to a plain dict for JSON/TypeScript output."""
        return {
            'item': self.item_name_id,
            'quantity': float(self.quantity),
            'reducible': self.reducible
        }
