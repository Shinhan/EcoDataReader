"""Crafting table model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CraftingTable:
    """A crafting station (e.g. Anvil, Sawmill) that recipes can be crafted at."""

    crafting_table_name: str
    crafting_table_name_id: str
    upgrade_module_tag: Optional[str] = None
    hidden: bool = False

    def to_dict(self):
        """Serialize this crafting table to a plain dict for JSON/TypeScript output."""
        return {
            'name': self.crafting_table_name,
            'nameID': self.crafting_table_name_id,
            'upgradeModuleType': self.upgrade_module_tag,
            'hidden': self.hidden
        }
