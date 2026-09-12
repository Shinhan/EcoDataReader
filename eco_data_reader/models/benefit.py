"""Benefit (talent) model."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AppliesTo:
    """The skills/item-tags/recipes/crafting-tables a Bonus's condition is scoped to."""

    skills: List[str] = field(default_factory=list)
    item_tags: List[str] = field(default_factory=list)
    recipes: List[str] = field(default_factory=list)
    crafting_tables: List[str] = field(default_factory=list)

    def to_dict(self):
        """Serialize this scope to a plain dict for JSON/TypeScript output."""
        return {
            'skills': self.skills,
            'itemTags': self.item_tags,
            'recipes': self.recipes,
            'craftingTables': self.crafting_tables
        }


@dataclass
class Bonus:
    """A single crafting-related effect (e.g. reduced resource cost) granted by a benefit,
    scoped by an AppliesTo condition."""

    action: str
    effect_type: str
    value: object
    applies_to: AppliesTo
    cap: Optional[float] = None

    def to_dict(self):
        """Serialize this bonus to a plain dict for JSON/TypeScript output."""
        return {
            'action': self.action,
            'effectType': self.effect_type,
            'value': self.value,
            'cap': self.cap,
            'appliesTo': self.applies_to.to_dict()
        }


@dataclass
class Benefit:
    """A talent granted by a skill at a given level, and the bonuses it confers."""

    name: str
    name_id: str
    skill_name_id: str
    level: int
    description: str = ""
    bonuses: List[Bonus] = field(default_factory=list)
    raw_value: Optional[float] = None

    def to_dict(self):
        """Serialize this benefit to a plain dict for JSON/TypeScript output."""
        return {
            'name': self.name,
            'nameID': self.name_id,
            'description': self.description,
            'skill': self.skill_name_id,
            'level': self.level,
            'rawValue': self.raw_value,
            'bonuses': [bonus.to_dict() for bonus in self.bonuses]
        }
