import os
import re
import logging
from pathlib import Path
from decimal import Decimal
from typing import Dict, List, Optional
from ..models import Item, Recipe, Ingredient, Output, CraftingTable, Skill, Benefit, Bonus, AppliesTo

logger = logging.getLogger(__name__)


class EcoServerFileService:
    ITEMS_LOCATION = "AutoGen\\"
    TAGS_LOCATION = "Systems\\TagDefinitions.cs"
    TALENT_GROUPS_FOLDER = "Benefit"
    BENEFITS_LOCATION = "Benefits"

    ITEM_FOLDERS = ["Block", "Clothing", "Fertilizer", "Food", "Item",
                    "PluginModule", "Seed", "Tool", "Vehicle", "WorldObject"]

    RECIPE_FOLDERS = ["Block", "Clothing", "Fertilizer", "Food", "Item",
                      "PluginModule", "Recipe", "Seed", "Tool", "Vehicle", "WorldObject"]

    CRAFTING_TABLE_FOLDERS = ["WorldObject"]
    SKILL_FOLDERS = ["Tech"]

    def __init__(self, eco_server_mods_core_path: str):
        self.eco_server_path = eco_server_mods_core_path

    def get_all_items(self) -> List[Item]:
        items = []

        for folder in self.ITEM_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    name = self._get_name_from_cs_file_contents(file_contents)
                    if name:
                        item_name_id = self._get_item_name_id_from_cs_file_contents(file_contents)
                        item_tags = self._get_item_tags_from_cs_file_contents(file_contents)
                        items.append(Item(
                            name=name,
                            item_name_id=item_name_id,
                            tags=item_tags,
                            image_file="UI_Icons_06.png",
                            x_pos=0,
                            y_pos=0
                        ))
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        items.sort(key=lambda x: x.item_name_id)
        return items

    def get_all_tags(self) -> List[Item]:
        tags = []

        try:
            tags_file = Path(self.eco_server_path) / self.TAGS_LOCATION
            with open(tags_file, 'r', encoding='utf-8') as f:
                file_contents = f.read()

            # Ignore hidden tags in tag definitions file
            hidden_index = file_contents.find("Hidden")
            if hidden_index != -1:
                file_contents = file_contents[:hidden_index]

            tag_regex = r'new TagDefinition\("([\w\s]+)"'
            matches = re.finditer(tag_regex, file_contents)

            for match in matches:
                tag_name = match.group(1)
                tag_name = tag_name.replace(" ", "")
                # Split by camel case
                tag_name_spaced = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', tag_name)).strip()
                tags.append(Item(
                    name=tag_name_spaced,
                    item_name_id=tag_name.replace(" ", ""),
                    tag=True
                ))
        except Exception as e:
            logger.error(f"Error reading tags: {e}")

        tags.sort(key=lambda x: x.item_name_id)
        return tags

    def get_all_recipes(self) -> List[Recipe]:
        recipes = []

        for folder in self.RECIPE_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    recipe = self._get_recipe_from_cs_file_contents(file_contents, file_path.name)
                    if recipe:
                        recipes.append(recipe)
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        recipes.sort(key=lambda x: x.name_id)
        return recipes

    def get_all_crafting_tables(self) -> List[CraftingTable]:
        crafting_tables = []

        for folder in self.CRAFTING_TABLE_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    crafting_table = self._get_crafting_table_from_cs_file_contents(
                        file_contents, file_path.name)
                    if crafting_table:
                        crafting_tables.append(crafting_table)
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        crafting_tables.sort(key=lambda x: x.crafting_table_name_id)
        return crafting_tables

    def get_all_skills(self) -> List[Skill]:
        skills = []

        for folder in self.SKILL_FOLDERS:
            folder_path = Path(self.eco_server_path) / self.ITEMS_LOCATION / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*.cs"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()

                    skill = self._get_skill_from_cs_file_contents(file_contents, file_path.name)
                    if skill:
                        skills.append(skill)
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

        skills.sort(key=lambda x: x.name_id)
        return skills

    def get_all_benefits(self) -> List[Benefit]:
        """Extract talents (skill benefits) that have a defined owning skill and level.

        Talent groups live in AutoGen\\Benefit\\*.cs (name, description, owning skill, level).
        Their crafting-related bonus math lives separately in Benefits\\*.cs, on the base
        Talent class each talent-group variant inherits from. Talents with no talent group
        (e.g. SampleTalents.cs) are skipped since they have no defined skill/level.
        """
        benefits = []

        benefits_dir = Path(self.eco_server_path) / self.BENEFITS_LOCATION
        bonuses_by_base_talent = self._get_bonuses_by_base_talent(benefits_dir)

        talent_groups_dir = Path(self.eco_server_path) / self.ITEMS_LOCATION / self.TALENT_GROUPS_FOLDER
        if not talent_groups_dir.exists():
            return benefits

        file_contents_list = []
        subclass_to_parent: Dict[str, str] = {}
        subclass_body_by_name: Dict[str, str] = {}

        for file_path in talent_groups_dir.glob("*.cs"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue

            file_contents_list.append(contents)

            for sub_match in re.finditer(r'class (\w+Talent) : (\w+Talent)\b', contents):
                subclass_name, parent_name = sub_match.group(1), sub_match.group(2)
                subclass_to_parent[subclass_name] = parent_name
                try:
                    body_open = contents.index('{', sub_match.end())
                    subclass_body_by_name[subclass_name] = self._extract_balanced(contents, body_open)
                except ValueError:
                    continue

        for contents in file_contents_list:
            benefits.extend(self._get_benefits_from_talent_group_file_contents(
                contents, bonuses_by_base_talent, subclass_to_parent, subclass_body_by_name))

        benefits.sort(key=lambda x: x.name_id)
        return benefits

    @staticmethod
    def _get_recipe_from_cs_file_contents(contents: str, file_name: str) -> Optional[Recipe]:
        # Recipe display name (e.g. Butcher Bison)
        recipe_name_regex = r'displayName:\s*Localizer\.DoStr\("([\w\s]+)"\)'
        match = re.search(recipe_name_regex, contents)
        if not match:
            logger.warning(f"Could not find recipe name for file {file_name}")
            return None
        recipe_name = match.group(1)

        # Recipe name ID (e.g. ButcherBison)
        recipe_name_id_regex = r'recipe.Init\(\n*\s*name:\s*"(\w+)"'
        match = re.search(recipe_name_id_regex, contents)
        if not match:
            logger.warning(f"Could not find recipe name ID for recipe {recipe_name}")
            return None
        recipe_name_id = match.group(1)

        ingredients = []

        # Recipe ingredients - Specific items (non-tag)
        recipe_ingredient_regex = r'new IngredientElement\(typeof\( *(\w+)\), (\d+(?:\.\d+)?)f?, *(\w+)'
        matches = re.finditer(recipe_ingredient_regex, contents)
        for match in matches:
            ingredient_name_id = match.group(1)
            quantity = Decimal(match.group(2))
            reducible = match.group(3).lower() == "typeof"
            ingredients.append(Ingredient(
                item_name_id=ingredient_name_id,
                quantity=quantity,
                reducible=reducible,
                tag=False
            ))

        # Recipe ingredients - tags
        tag_recipe_ingredients_regex = r'new IngredientElement\("([\w\s]+)", *(\d+), *(\w+)'
        matches = re.finditer(tag_recipe_ingredients_regex, contents)
        for match in matches:
            tag_ingredient_name_id = match.group(1).replace(" ", "")
            quantity = Decimal(match.group(2))
            reducible = match.group(3).lower() == "typeof"
            ingredients.append(Ingredient(
                item_name_id=tag_ingredient_name_id,
                quantity=quantity,
                reducible=reducible,
                tag=True
            ))

        if not ingredients:
            logger.warning(f"Could not find ingredients for recipe {recipe_name}")

        outputs = []

        # Recipe outputs
        recipe_outputs_regex = r'new CraftingElement<(\w+)>\((\d*\.?\d*)f?\)'
        matches = re.finditer(recipe_outputs_regex, contents)
        output_count = 0
        for match in matches:
            output_item_name_id = match.group(1)
            quantity_string = match.group(2)
            quantity = Decimal(1) if not quantity_string else Decimal(quantity_string)
            output = Output(
                item_name_id=output_item_name_id,
                quantity=quantity,
                reducible=False,
                primary=(output_count == 0)
            )
            outputs.append(output)
            output_count += 1

        if not outputs:
            logger.warning(f"Could not find outputs for recipe {recipe_name}")

        # Recipe outputs - secondary (e.g. Tailings, Slag, Barrel)
        recipe_outputs_waste_regex = r'new CraftingElement<(\w+)>\(typeof\(\w+\), (\d+)(,?)'
        matches = re.finditer(recipe_outputs_waste_regex, contents)
        for match in matches:
            output_item_name_id = match.group(1)
            quantity = Decimal(match.group(2))
            reducible = bool(match.group(3)) or "Tailings" in output_item_name_id or "Slag" in output_item_name_id
            outputs.append(Output(
                item_name_id=output_item_name_id,
                quantity=quantity,
                reducible=reducible
            ))

        # Skill and level
        skill_level_regex = r'\[RequiresSkill\(typeof\((\w+)\), (\d)'
        match = re.search(skill_level_regex, contents)
        if match:
            skill_name_id = match.group(1)
            level = int(match.group(2))
        else:
            logger.warning(f"Could not find skill and level for recipe {recipe_name}, assuming SelfImprovement")
            skill_name_id = "SelfImprovementSkill"
            level = 0

        # Labor cost
        labor_regex = r'CreateLaborInCaloriesValue\((\d+)'
        match = re.search(labor_regex, contents)
        if match:
            labor = int(match.group(1))
        else:
            logger.warning(f"Could not find labor cost for recipe {recipe_name}")
            labor = 0

        # Crafting table
        crafting_table_regex = r'CraftingComponent\.AddRecipe\(tableType:\s*typeof\((\w+)\)'
        match = re.search(crafting_table_regex, contents)
        if match:
            crafting_table_name_id = match.group(1)
        else:
            logger.warning(f"Could not find crafting table for recipe {recipe_name}")
            crafting_table_name_id = ""

        return Recipe(
            name=recipe_name,
            name_id=recipe_name_id,
            skill_name_id=skill_name_id,
            level=level,
            labor=labor,
            crafting_table_name_id=crafting_table_name_id,
            ingredients=ingredients,
            outputs=outputs
        )

    @staticmethod
    def _get_name_from_cs_file_contents(contents: str) -> Optional[str]:
        name_search_regex = r'LocDisplayName\("([\w\s]+)"'
        match = re.search(name_search_regex, contents)
        return match.group(1) if match else None

    @staticmethod
    def _get_item_name_id_from_cs_file_contents(contents: str) -> Optional[str]:
        name_search_regex = r'public partial class (\w+Item)'
        match = re.search(name_search_regex, contents)
        return match.group(1) if match else None

    @staticmethod
    def _get_item_tags_from_cs_file_contents(contents: str) -> List[str]:
        """Extract the item-category tags (e.g. [Tag("Housing")]) applied to an item's class,
        matching the same name-ID form (spaces stripped) used by get_all_tags().

        Some files (e.g. Block/*.cs) define several classes - the item's own attribute block sits
        directly above its class declaration, so we scan backwards from there rather than
        searching the whole file, to avoid picking up [Tag(...)] attributes from other classes."""
        class_match = re.search(r'public partial class \w+Item\b', contents)
        if not class_match:
            return []

        attribute_line_regex = re.compile(r'^(?:\[[^\]]*\])+\s*(?://.*)?$')
        attribute_lines = []
        for line in reversed(contents[:class_match.start()].splitlines()):
            stripped = line.strip()
            if not stripped:
                continue
            if attribute_line_regex.match(stripped):
                attribute_lines.append(line)
            else:
                break

        tag_regex = r'\[Tag\("([\w\s]+)"\)\]'
        return [match.replace(" ", "") for match in re.findall(tag_regex, '\n'.join(attribute_lines))]

    @staticmethod
    def _get_skill_from_cs_file_contents(file_contents: str, file_name: str) -> Optional[Skill]:
        skill_search_regex = r'Tag\("Specialty"\)'
        if not re.search(skill_search_regex, file_contents):
            return None

        name_id_search_regex = r'public partial class (\w+Skill) : Skill'
        match = re.search(name_id_search_regex, file_contents)
        if not match:
            logger.warning(f"Could not find skill name ID for file {file_name}")
            return None
        name_id = match.group(1)

        name = file_name.replace(".cs", "")
        # Split by camel case
        name = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).strip()

        return Skill(name=name, name_id=name_id)

    @staticmethod
    def _get_crafting_table_from_cs_file_contents(file_contents: str, file_name: str) -> Optional[CraftingTable]:
        crafting_search_regex = r'RequireComponent\(typeof\(CraftingComponent'
        if not re.search(crafting_search_regex, file_contents):
            return None

        name_search_regex = r'DisplayName\s+=>\s+Localizer\.DoStr\("([\w\s]+)"\)'
        match = re.search(name_search_regex, file_contents)
        if not match:
            logger.warning(f"Could not find crafting table name for file {file_name}")
            return None
        name = match.group(1)

        name_id_search_regex = r'public partial class (\w+Object)'
        match = re.search(name_id_search_regex, file_contents)
        if not match:
            logger.warning(f"Could not find nameID for crafting table {name}")
            return None
        name_id = match.group(1)

        upgrade_module_search_regex = r'AllowPluginModules\(Tags = new\[] \{ "(\w+)'
        match = re.search(upgrade_module_search_regex, file_contents)
        upgrade_module = match.group(1) if match else None

        return CraftingTable(
            crafting_table_name=name,
            crafting_table_name_id=name_id,
            upgrade_module_tag=upgrade_module
        )

    @staticmethod
    def _extract_balanced(text: str, open_brace_index: int) -> str:
        """Return the text between text[open_brace_index] ('{') and its matching '}'."""
        depth = 0
        for i in range(open_brace_index, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return text[open_brace_index + 1:i]
        return text[open_brace_index + 1:]

    @classmethod
    def _get_bonuses_by_base_talent(cls, benefits_dir: Path) -> Dict[str, List[Bonus]]:
        """Scan Benefits\\*.cs for classes that inherit directly from Talent and hold the
        actual Bonus (Causes/Effects) definitions, keyed by class name."""
        bonuses_by_talent: Dict[str, List[Bonus]] = {}
        if not benefits_dir.exists():
            return bonuses_by_talent

        class_regex = re.compile(r'class (\w+Talent) : Talent\b')

        for file_path in benefits_dir.glob("*.cs"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue

            for class_match in class_regex.finditer(contents):
                talent_name = class_match.group(1)
                try:
                    body_open = contents.index('{', class_match.end())
                except ValueError:
                    continue
                class_body = cls._extract_balanced(contents, body_open)

                bonuses = cls._parse_bonuses_from_class_body(class_body)
                if bonuses:
                    bonuses_by_talent.setdefault(talent_name, []).extend(bonuses)

        return bonuses_by_talent

    @classmethod
    def _parse_bonuses_from_class_body(cls, class_body: str) -> List[Bonus]:
        bonuses = []
        for bonus_match in re.finditer(r'new Bonus\s*', class_body):
            try:
                brace_index = class_body.index('{', bonus_match.end())
            except ValueError:
                continue
            # Skip if something other than whitespace sits between "new Bonus" and the brace
            if class_body[bonus_match.end():brace_index].strip():
                continue
            bonus_block = cls._extract_balanced(class_body, brace_index)
            bonus = cls._parse_single_bonus(bonus_block)
            if bonus:
                bonuses.append(bonus)
        return bonuses

    @classmethod
    def _parse_single_bonus(cls, bonus_block: str) -> Optional[Bonus]:
        # Only surface bonuses caused by crafting (resource cost, craft time, labor,
        # power, yield, unlocks, etc.) - other cause types (harvest, tool-use, area,
        # profession) aren't representable in this schema and are skipped.
        craft_cause_match = re.search(r'new CraftBonusCause\s*', bonus_block)
        if not craft_cause_match:
            return None
        try:
            cause_brace = bonus_block.index('{', craft_cause_match.end())
        except ValueError:
            return None
        cause_block = cls._extract_balanced(bonus_block, cause_brace)

        action_match = re.search(r'Action\s*=\s*BonusAction\.(\w+)', cause_block)
        if not action_match:
            return None
        action = action_match.group(1)

        applies_to = AppliesTo(
            skills=cls._extract_hashset_typeof_names(cause_block, 'SkillTypes'),
            recipes=cls._extract_hashset_typeof_names(cause_block, 'Recipes'),
            crafting_tables=cls._extract_hashset_typeof_names(cause_block, 'CraftStationTypes'),
            item_tags=cls._extract_hashset_quoted_strings(cause_block, 'ItemTags')
        )

        effect_match = re.search(r'new (BonusEffect\w+)\s*', bonus_block)
        if not effect_match:
            return None
        try:
            effect_brace = bonus_block.index('{', effect_match.end())
        except ValueError:
            return None
        effect_block = cls._extract_balanced(bonus_block, effect_brace)
        effect_class = effect_match.group(1)

        value_match = re.search(r'Value\s*=\s*(-?\d*\.?\d+)f?', effect_block)
        raw_value = float(value_match.group(1)) if value_match else None

        cap = None
        if effect_class in ('BonusEffectMultiplicative', 'BonusEffectCappedMultiplicative'):
            effect_type = 'CappedMultiplicative' if effect_class == 'BonusEffectCappedMultiplicative' else 'Multiplicative'
            value = round((raw_value - 1) * 100, 4) if raw_value is not None else 0.0
            if effect_type == 'CappedMultiplicative':
                cap_match = re.search(r'Cap\s*=\s*(-?\d*\.?\d+)f?', effect_block)
                if cap_match:
                    cap = round((float(cap_match.group(1)) - 1) * 100, 4)
        elif effect_class == 'BonusEffectAdditive':
            effect_type = 'Additive'
            value = raw_value if raw_value is not None else 0.0
        elif effect_class == 'BonusEffectOverride':
            effect_type = 'Override'
            value = True
        else:
            # Diminishing, Chance, etc. aren't representable as a flat value - skip
            return None

        return Bonus(action=action, effect_type=effect_type, value=value, cap=cap, applies_to=applies_to)

    @staticmethod
    def _extract_hashset_typeof_names(cause_block: str, field_name: str) -> List[str]:
        field_match = re.search(field_name + r'\s*=\s*new HashSet<[^>]*>\s*\{([^}]*)\}', cause_block)
        if not field_match:
            return []
        return re.findall(r'typeof\((\w+)\)', field_match.group(1))

    @staticmethod
    def _extract_hashset_quoted_strings(cause_block: str, field_name: str) -> List[str]:
        field_match = re.search(field_name + r'\s*=\s*new HashSet<[^>]*>\s*\{([^}]*)\}', cause_block)
        if not field_match:
            return []
        return re.findall(r'"([^"]+)"', field_match.group(1))

    @classmethod
    def _get_benefits_from_talent_group_file_contents(
            cls, contents: str,
            bonuses_by_base_talent: Dict[str, List[Bonus]],
            subclass_to_parent: Dict[str, str],
            subclass_body_by_name: Dict[str, str]) -> List[Benefit]:
        benefits = []

        talent_group_regex = re.compile(
            r'\[LocDisplayName\("([^"]+)"\)\]\s*'
            r'(?:\[LocDescription\("([^"]+)"\)\]\s*)?'
            r'public partial class (\w+TalentGroup) : TalentGroup'
        )

        for group_match in talent_group_regex.finditer(contents):
            display_name, description, group_class_name = group_match.groups()
            description = description or ""

            try:
                body_open = contents.index('{', group_match.end())
            except ValueError:
                continue
            group_body = cls._extract_balanced(contents, body_open)

            skill_match = re.search(r'OwningSkill\s*=\s*typeof\((\w+)\)', group_body)
            if not skill_match:
                logger.debug(f"Skipping talent group {group_class_name}: no OwningSkill defined")
                continue
            skill_name_id = skill_match.group(1)

            level_match = re.search(r'\.Level\s*=\s*(\d+)', group_body)
            level = int(level_match.group(1)) if level_match else 0

            talent_type_names = re.findall(r'typeof\((\w+Talent)\)', group_body)

            bonuses: List[Bonus] = []
            raw_value = None
            for talent_type_name in talent_type_names:
                base_name = subclass_to_parent.get(talent_type_name, talent_type_name)
                if base_name in bonuses_by_base_talent:
                    bonuses.extend(bonuses_by_base_talent[base_name])
                elif talent_type_name in subclass_body_by_name:
                    value_match = re.search(r'\.Value\s*=\s*(-?\d*\.?\d+)f?', subclass_body_by_name[talent_type_name])
                    if value_match:
                        raw_value = float(value_match.group(1))

            benefits.append(Benefit(
                name=display_name,
                name_id=group_class_name,
                skill_name_id=skill_name_id,
                level=level,
                description=description,
                bonuses=bonuses,
                raw_value=raw_value
            ))

        return benefits
