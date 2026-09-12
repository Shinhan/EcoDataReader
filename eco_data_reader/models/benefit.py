from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AppliesTo:
    skills: List[str] = field(default_factory=list)
    item_tags: List[str] = field(default_factory=list)
    recipes: List[str] = field(default_factory=list)
    crafting_tables: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            'skills': self.skills,
            'itemTags': self.item_tags,
            'recipes': self.recipes,
            'craftingTables': self.crafting_tables
        }


@dataclass
class Bonus:
    action: str
    effect_type: str
    value: object
    applies_to: AppliesTo
    cap: Optional[float] = None

    def to_dict(self):
        return {
            'action': self.action,
            'effectType': self.effect_type,
            'value': self.value,
            'cap': self.cap,
            'appliesTo': self.applies_to.to_dict()
        }


@dataclass
class Benefit:
    name: str
    name_id: str
    skill_name_id: str
    level: int
    description: str = ""
    bonuses: List[Bonus] = field(default_factory=list)
    raw_value: Optional[float] = None

    def to_dict(self):
        return {
            'name': self.name,
            'nameID': self.name_id,
            'description': self.description,
            'skill': self.skill_name_id,
            'level': self.level,
            'rawValue': self.raw_value,
            'bonuses': [bonus.to_dict() for bonus in self.bonuses]
        }
