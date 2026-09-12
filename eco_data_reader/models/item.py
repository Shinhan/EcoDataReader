from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Item:
    name: str
    item_name_id: str
    tag: bool = False
    tags: List[str] = field(default_factory=list)
    image_file: str = "UI_Icons_06.png"
    x_pos: int = 0
    y_pos: int = 0

    EQUIVALENT_ITEM_NAME_IDS: List[Tuple[str, str]] = field(default_factory=lambda: [
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
    ], repr=False, compare=False, hash=False)

    @staticmethod
    def name_ids_match(item_name_id: str, other_item_name_id: str) -> bool:
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
        return old_item.name == new_item.name and old_item.item_name_id == new_item.item_name_id

    def to_dict(self):
        return {
            'name': self.name,
            'nameID': self.item_name_id,
            'tag': self.tag,
            'tags': self.tags,
            'imageFile': self.image_file,
            'xPos': self.x_pos,
            'yPos': self.y_pos
        }
