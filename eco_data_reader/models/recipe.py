"""Recipe model."""

from dataclasses import dataclass, field
from typing import List
import logging
from .ingredient import Ingredient
from .output import Output

logger = logging.getLogger(__name__)


@dataclass
class Recipe:
    """A crafting recipe: the skill/level, labor, crafting table, ingredients and outputs."""

    name: str
    name_id: str
    skill_name_id: str
    level: int
    labor: int
    crafting_table_name_id: str
    ingredients: List[Ingredient] = field(default_factory=list)
    outputs: List[Output] = field(default_factory=list)
    hidden: bool = False

    def to_readable_string(self) -> str:
        """Format this recipe as a multi-line human-readable summary."""
        result = f"{self.name} ({self.name_id})\n"
        result += f"{self.labor} calories of level {self.level} {self.skill_name_id.replace('Skill', '')} "
        result += f"labor at {self.crafting_table_name_id.replace('Object', '')}\n"
        result += "Ingredients:\n"
        for ingredient in self.ingredients:
            result += f"{ingredient}\n"
        result += "Produces:\n"
        for output in self.outputs:
            result += f"{output}\n"
        return result

    @staticmethod
    def recipes_are_equal(old_recipe: 'Recipe', new_recipe: 'Recipe') -> bool:
        """Compare two recipes for changes, logging each differing field along the way."""
        if old_recipe == new_recipe:
            return False

        if old_recipe.name != new_recipe.name:
            Recipe._log_diff("name", old_recipe.name, new_recipe.name, new_recipe.name)

        if old_recipe.skill_name_id != new_recipe.skill_name_id:
            Recipe._log_diff("skill", old_recipe.skill_name_id, new_recipe.skill_name_id, new_recipe.name)

        if old_recipe.level != new_recipe.level:
            Recipe._log_diff("level", old_recipe.level, new_recipe.level, new_recipe.name)

        if old_recipe.labor != new_recipe.labor:
            Recipe._log_diff("labor", old_recipe.labor, new_recipe.labor, new_recipe.name)

        if old_recipe.crafting_table_name_id != new_recipe.crafting_table_name_id:
            Recipe._log_diff("craftingTable", old_recipe.crafting_table_name_id,
                           new_recipe.crafting_table_name_id, new_recipe.name)

        old_ingredients = sorted(old_recipe.ingredients, key=lambda i: i.item_name_id)
        new_ingredients = sorted(new_recipe.ingredients, key=lambda i: i.item_name_id)
        if old_ingredients != new_ingredients:
            old_ing_strings = [ing.to_readable_string() for ing in old_ingredients]
            new_ing_strings = [ing.to_readable_string() for ing in new_ingredients]
            Recipe._log_diff("ingredients", old_ing_strings, new_ing_strings, new_recipe.name)

        old_outputs = sorted(old_recipe.outputs, key=lambda o: o.item_name_id)
        new_outputs = sorted(new_recipe.outputs, key=lambda o: o.item_name_id)
        if old_outputs != new_outputs:
            old_out_strings = [out.to_readable_string() for out in old_outputs]
            new_out_strings = [out.to_readable_string() for out in new_outputs]
            Recipe._log_diff("outputs", old_out_strings, new_out_strings, new_recipe.name)

        return True

    @staticmethod
    def _log_diff(prop_name: str, old, newer, recipe_name: str):
        """Log a single changed field for a recipe."""
        logger.info(f"{recipe_name} {prop_name}: {old} -> {newer}")

    def to_dict(self):
        """Serialize this recipe to a plain dict for JSON/TypeScript output."""
        return {
            'name': self.name,
            'nameID': self.name_id,
            'skill': self.skill_name_id,
            'level': self.level,
            'labor': self.labor,
            'craftingTable': self.crafting_table_name_id,
            'hidden': self.hidden,
            'ingredients': [ing.to_dict() for ing in self.ingredients],
            'outputs': [out.to_dict() for out in self.outputs]
        }
