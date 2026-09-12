"""Item data model, including the item-tag equivalence rules used to reconcile
name IDs that refer to the same underlying item under different names."""

from dataclasses import dataclass, field
from typing import ClassVar, List, Tuple


@dataclass
class Item:
    """A craftable item, or a tag definition (when tag=True), scraped from the Eco server."""

    name: str
    item_name_id: str
    tag: bool = False
    tags: List[str] = field(default_factory=list)
    image_file: str = "UI_Icons_06.png"
    x_pos: int = 0
    y_pos: int = 0

    EQUIVALENT_ITEM_NAME_IDS: ClassVar[List[Tuple[str, str]]] = [
        ("WoodBoard", "BoardItem"),
        ("Oil", "OilItem"),
        ("AshlarStone", "AshlarBasaltItem"),
        ("AshlarStone", "AshlarGneissItem"),
        ("AshlarStone", "AshlarGraniteItem"),
        ("AshlarStone", "AshlarLimestoneItem"),
        ("AshlarStone", "AshlarSandstoneItem"),
        ("AshlarStone", "AshlarShaleItem"),
        ("HewnLog", "HewnLogItem"),
        ("CompositeLumber", "CompositeLumberItem"),
        ("Lumber", "LumberItem")
    ]

    @staticmethod
    def name_ids_match(item_name_id: str, other_item_name_id: str) -> bool:
        """Check whether two item name IDs refer to the same underlying item."""
        if item_name_id == other_item_name_id:
            return True

        equivalent_ids = [
            ("WoodBoard", "BoardItem"),
            ("Oil", "OilItem"),
            ("AshlarStone", "AshlarBasaltItem"),
            ("AshlarStone", "AshlarGneissItem"),
            ("AshlarStone", "AshlarGraniteItem"),
            ("AshlarStone", "AshlarLimestoneItem"),
            ("AshlarStone", "AshlarSandstoneItem"),
            ("AshlarStone", "AshlarShaleItem"),
            ("HewnLog", "HewnLogItem"),
            ("CompositeLumber", "CompositeLumberItem"),
            ("Lumber", "LumberItem")
        ]

        for left, right in equivalent_ids:
            if (left == item_name_id and right == other_item_name_id) or \
               (right == item_name_id and left == other_item_name_id):
                return True
        return False

    @staticmethod
    def items_are_equal(old_item: 'Item', new_item: 'Item') -> bool:
        """Check whether two Item instances represent the same item (by name and name ID)."""
        return old_item.name == new_item.name and old_item.item_name_id == new_item.item_name_id

    def to_dict(self):
        """Serialize this item to a plain dict for JSON/TypeScript output."""
        return {
            'name': self.name,
            'nameID': self.item_name_id,
            'tag': self.tag,
            'tags': self.tags,
            'imageFile': self.image_file,
            'xPos': self.x_pos,
            'yPos': self.y_pos
        }
