"""Skill model."""

from dataclasses import dataclass


@dataclass
class Skill:
    """A player skill (e.g. Carpentry) that recipes and benefits can be tied to."""

    name: str
    name_id: str

    def to_dict(self):
        """Serialize this skill to a plain dict for JSON/TypeScript output."""
        return {
            'name': self.name,
            'nameID': self.name_id
        }
