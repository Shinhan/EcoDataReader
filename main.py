#!/usr/bin/env python3
"""
Eco Data Reader - Python Version

Main entry point for reading and processing Eco server game data.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List

from eco_data_reader.config import Config
from eco_data_reader.services import EcoServerFileService
from eco_data_reader.models import Item, Recipe, Benefit
from eco_data_reader.utils import JsonTypeScriptProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_references(all_items: List[Item], all_tags: List[Item], all_skills,
                         all_crafting_tables, all_recipes: List[Recipe],
                         all_benefits: List[Benefit]) -> List[str]:
    """Check that every cross-reference in the scraped data resolves to a real nameID.

    getItemByNameID/getSkillByNameID/getCraftingTableByNameID only console.error on a miss
    and keep going at runtime in EcoCraftingTool, so a bad reference here would otherwise
    become bad runtime data with no build failure. Returns a list of human-readable problem
    descriptions (empty if everything resolves)."""
    item_ids = {item.item_name_id for item in all_items} | {tag.item_name_id for tag in all_tags}
    skill_ids = {skill.name_id for skill in all_skills}
    crafting_table_ids = {table.crafting_table_name_id for table in all_crafting_tables}
    recipe_ids = {recipe.name_id for recipe in all_recipes}

    problems = []

    for recipe in all_recipes:
        if recipe.skill_name_id not in skill_ids:
            problems.append(f"Recipe '{recipe.name_id}' references unknown skill '{recipe.skill_name_id}'")
        if recipe.crafting_table_name_id not in crafting_table_ids:
            problems.append(f"Recipe '{recipe.name_id}' references unknown crafting table "
                             f"'{recipe.crafting_table_name_id}'")
        for ingredient in recipe.ingredients:
            if ingredient.item_name_id not in item_ids:
                problems.append(f"Recipe '{recipe.name_id}' ingredient references unknown item "
                                 f"'{ingredient.item_name_id}'")
        for output in recipe.outputs:
            if output.item_name_id not in item_ids:
                problems.append(f"Recipe '{recipe.name_id}' output references unknown item "
                                 f"'{output.item_name_id}'")

    for benefit in all_benefits:
        for bonus in benefit.bonuses:
            for recipe_name_id in bonus.applies_to.recipes:
                if recipe_name_id not in recipe_ids:
                    problems.append(f"Benefit '{benefit.name_id}' applies to unknown recipe "
                                     f"'{recipe_name_id}'")

    return problems


def compare_items_and_recipes():
    """Compare current items and recipes with the latest from the Eco server."""
    config = Config()
    eco_server_service = EcoServerFileService(config.eco_server_path)

    logger.info("Loading recipes from Eco server...")
    recipes = eco_server_service.get_all_recipes()
    logger.info(f"Loaded {len(recipes)} recipes")

    logger.info("Loading items from Eco server...")
    items = eco_server_service.get_all_items()
    logger.info(f"Loaded {len(items)} items")

    # For now, just output the data as JSON
    # In future, implement comparison with crafting tool data
    logger.info("Conversion complete!")


def get_locale_json() -> str:
    """Generate locale data from the defaultstrings.csv file."""
    # This would need implementation similar to the Translator class
    # For now, returning placeholder
    logger.warning("Locale JSON generation not yet implemented")
    return "{}"


def write_items_to_file():
    """Write current items list to file."""
    config = Config()
    items = get_items_from_files(config)

    output_file = Path("resources") / "newest-items.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(f"{item.name}\n")

    logger.info(f"Wrote {len(items)} items to {output_file}")


def write_recipes_to_file():
    """Write current recipes list to file."""
    config = Config()
    recipes = get_recipes_from_files(config)

    output_file = Path("resources") / "newest-recipes.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for recipe in recipes:
            f.write(f"{recipe.name}\n")

    logger.info(f"Wrote {len(recipes)} recipes to {output_file}")


def generate_new_recipes_string() -> str:
    """Generate TypeScript string for new recipes."""
    config = Config()
    new_recipes = get_recipes_from_files(config)

    # Convert to JSON
    recipes_data = [recipe.to_dict() for recipe in new_recipes]
    recipe_json = json.dumps(recipes_data, indent=2)

    # Convert to TypeScript format
    ts_string = JsonTypeScriptProcessor.process_json_to_typescript(recipe_json)

    # Remove [ ] from the ends
    ts_string = ts_string[1:-1]

    logger.info("Generated TypeScript string for new recipes")
    return ts_string


def generate_new_items_string() -> str:
    """Generate TypeScript string for new items."""
    config = Config()
    new_items = get_items_from_files(config)

    # Convert to JSON
    items_data = [item.to_dict() for item in new_items]
    item_json = json.dumps(items_data, indent=2)

    # Convert to TypeScript format
    ts_string = JsonTypeScriptProcessor.process_json_to_typescript(item_json)

    # Remove [ ] from the ends
    ts_string = ts_string[1:-1]

    logger.info("Generated TypeScript string for new items")
    return ts_string


def get_recipes_from_files(config: Config) -> List[Recipe]:
    """Get recipes from Eco server files that are not in current-recipes.txt."""
    eco_server_service = EcoServerFileService(config.eco_server_path)
    recipes = eco_server_service.get_all_recipes()
    recipes.sort(key=lambda r: r.name)

    new_recipes = []
    for recipe in recipes:
        if matches_new_recipes(recipe):
            new_recipes.append(recipe)

    return new_recipes


def get_items_from_files(config: Config) -> List[Item]:
    """Get items from Eco server files that are not in current-items.txt."""
    eco_server_service = EcoServerFileService(config.eco_server_path)
    items = eco_server_service.get_all_items()
    items.sort(key=lambda i: i.name)

    new_items = []
    for item in items:
        if matches_new_items(item):
            new_items.append(item)

    return new_items


def matches_new_items(item: Item) -> bool:
    """Check if item is not in current-items.txt."""
    current_items_file = Path("src/main/resources/current-items.txt")
    if not current_items_file.exists():
        return True

    with open(current_items_file, 'r', encoding='utf-8') as f:
        item_names = [line.strip() for line in f if line.strip()]

    return not any(name.lower() == item.name.lower() for name in item_names)


def matches_new_recipes(recipe: Recipe) -> bool:
    """Check if recipe is not in current-recipes.txt."""
    current_recipes_file = Path("src/main/resources/current-recipes.txt")
    if not current_recipes_file.exists():
        return True

    with open(current_recipes_file, 'r', encoding='utf-8') as f:
        recipe_names = [line.strip() for line in f if line.strip()]

    return not any(name.lower() == recipe.name.lower() for name in recipe_names)


def get_user_choice():
    """Get user's choice for what to generate."""
    print("\n" + "=" * 60)
    print("ECO DATA READER - OUTPUT OPTIONS")
    print("=" * 60)
    print("\nWhat would you like to generate?")
    print("\n1. All items and recipes (complete dataset)")
    print("2. Only NEW items and recipes (not in current-items.txt/current-recipes.txt)")
    print("3. Exit without generating")
    print("\n" + "=" * 60)

    while True:
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")


def generate_output_files(generate_all=True):
    """Generate output files based on user choice."""
    config = Config()
    eco_server_service = EcoServerFileService(config.eco_server_path)

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    logger.info("\n" + "=" * 60)
    logger.info(f"Generating {'ALL' if generate_all else 'NEW'} items and recipes...")
    logger.info("=" * 60)

    # Get items and recipes
    logger.info("\nLoading items from Eco server...")
    all_items = eco_server_service.get_all_items()
    all_items.sort(key=lambda i: i.name)
    logger.info(f"Loaded {len(all_items)} items")

    logger.info("\nLoading recipes from Eco server...")
    all_recipes = eco_server_service.get_all_recipes()
    all_recipes.sort(key=lambda r: r.name)
    logger.info(f"Loaded {len(all_recipes)} recipes")

    logger.info("\nLoading benefits from Eco server...")
    all_benefits = eco_server_service.get_all_benefits()
    logger.info(f"Loaded {len(all_benefits)} benefits")

    logger.info("\nLoading tags, skills, and crafting tables from Eco server...")
    all_tags = eco_server_service.get_all_tags()
    all_skills = eco_server_service.get_all_skills()
    all_crafting_tables = eco_server_service.get_all_crafting_tables()
    logger.info(f"Loaded {len(all_tags)} tags, {len(all_skills)} skills, "
                f"{len(all_crafting_tables)} crafting tables")

    logger.info("\nValidating cross-references...")
    reference_problems = validate_references(
        all_items, all_tags, all_skills, all_crafting_tables, all_recipes, all_benefits)
    if reference_problems:
        # Warn rather than abort: get_all_items()/get_all_skills()/get_all_crafting_tables() only
        # scan AutoGen\<folder>\*.cs, so hand-written classes living directly under Items\ or
        # Tools\ (e.g. DirtItem, SandItem) are legitimately invisible to this tool and will
        # always show up here even though they're valid in-game items - that's a scraper
        # coverage gap, not necessarily a bad reference. Still surface it loudly so a genuine
        # mistake (e.g. a typo'd nameID, or the PirozhokRecipe-style suffix bug) doesn't slip by.
        logger.warning(f"\nFound {len(reference_problems)} unresolved reference(s) - output will "
                        "still be generated, but double check these aren't typos:")
        for problem in reference_problems:
            logger.warning(f"  - {problem}")
    else:
        logger.info("All references resolved.")

    # Filter if needed
    if generate_all:
        items_to_generate = all_items
        recipes_to_generate = all_recipes
    else:
        logger.info("\nFiltering for new items only...")
        items_to_generate = [item for item in all_items if matches_new_items(item)]
        recipes_to_generate = [recipe for recipe in all_recipes if matches_new_recipes(recipe)]
        logger.info(f"Found {len(items_to_generate)} new items")
        logger.info(f"Found {len(recipes_to_generate)} new recipes")

    # Write item names list
    items_list_file = output_dir / ("all-items.txt" if generate_all else "new-items.txt")
    with open(items_list_file, 'w', encoding='utf-8') as f:
        for item in items_to_generate:
            f.write(f"{item.name}\n")
    logger.info(f"\n✓ Wrote items list to: {items_list_file}")

    # Write recipe names list
    recipes_list_file = output_dir / ("all-recipes.txt" if generate_all else "new-recipes.txt")
    with open(recipes_list_file, 'w', encoding='utf-8') as f:
        for recipe in recipes_to_generate:
            f.write(f"{recipe.name}\n")
    logger.info(f"✓ Wrote recipes list to: {recipes_list_file}")

    # Generate TypeScript for items
    items_data = [item.to_dict() for item in items_to_generate]
    item_json = json.dumps(items_data, indent=2)
    item_ts = JsonTypeScriptProcessor.process_json_to_typescript(item_json)

    items_ts_file = output_dir / ("all-items.ts" if generate_all else "new-items.ts")
    with open(items_ts_file, 'w', encoding='utf-8') as f:
        if generate_all:
            f.write(JsonTypeScriptProcessor.wrap_module(
                imports=["import {IItem, Item} from '../../app/model/item';"],
                array_export_name="itemsArray",
                item_type="IItem",
                array_ts=item_ts,
                map_export_name="items",
                class_name="Item",
                map_lambda_var="item"
            ))
        else:
            # A partial snippet meant to be merged by hand into the existing itemsArray,
            # so it isn't wrapped as a standalone module (its Map would only cover the new items).
            f.write("// Generated by Eco Data Reader\n")
            f.write("// New items for EcoCraftingTool - merge into items.ts\n\n")
            f.write("const items = ")
            f.write(item_ts)
            f.write(";\n")
    logger.info(f"✓ Wrote items TypeScript to: {items_ts_file}")

    # Generate TypeScript for recipes
    recipes_data = [recipe.to_dict() for recipe in recipes_to_generate]
    recipe_json = json.dumps(recipes_data, indent=2)
    recipe_ts = JsonTypeScriptProcessor.process_json_to_typescript(recipe_json)

    recipes_ts_file = output_dir / ("all-recipes.ts" if generate_all else "new-recipes.ts")
    with open(recipes_ts_file, 'w', encoding='utf-8') as f:
        if generate_all:
            f.write(JsonTypeScriptProcessor.wrap_module(
                imports=[
                    "import {getCraftingTableByNameID, getItemByNameID, getSkillByNameID} "
                    "from './util/data-utils';",
                    "import {IRecipe, Recipe} from '../../app/model/recipe';"
                ],
                array_export_name="recipesArray",
                item_type="IRecipe",
                array_ts=recipe_ts,
                map_export_name="recipes",
                class_name="Recipe",
                map_lambda_var="recipe"
            ))
        else:
            # A partial snippet meant to be merged by hand into the existing recipesArray,
            # so it isn't wrapped as a standalone module (its Map would only cover the new recipes).
            f.write("// Generated by Eco Data Reader\n")
            f.write("// New recipes for EcoCraftingTool - merge into recipes.ts\n\n")
            f.write("const recipes = ")
            f.write(recipe_ts)
            f.write(";\n")
    logger.info(f"✓ Wrote recipes TypeScript to: {recipes_ts_file}")

    # Generate TypeScript for benefits
    benefits_data = [benefit.to_dict() for benefit in all_benefits]
    benefit_json = json.dumps(benefits_data, indent=2)
    benefit_ts = JsonTypeScriptProcessor.process_json_to_typescript(benefit_json)

    benefits_ts_file = output_dir / "all-benefits.ts"
    with open(benefits_ts_file, 'w', encoding='utf-8') as f:
        f.write(JsonTypeScriptProcessor.wrap_module(
            imports=["import {Benefit, IBenefit} from '../../app/model/benefit';"],
            array_export_name="benefitsArray",
            item_type="IBenefit",
            array_ts=benefit_ts,
            map_export_name="benefits",
            class_name="Benefit",
            map_lambda_var="benefit",
            header_comment=(
                "//Generated from the Eco server's talent/benefit definitions. Recipe references have the\n"
                "//'Recipe' suffix stripped to match this project's recipe nameID convention (see recipes.ts)."
            )
        ))
    logger.info(f"✓ Wrote benefits TypeScript to: {benefits_ts_file}")

    logger.info("\n" + "=" * 60)
    logger.info("GENERATION COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"\nAll files saved to: {output_dir.absolute()}")
    logger.info(f"\n  Items:    {len(items_to_generate)}")
    logger.info(f"  Recipes:  {len(recipes_to_generate)}")
    logger.info(f"  Benefits: {len(all_benefits)}")
    logger.info("\nGenerated files:")
    logger.info(f"  - {items_list_file.name}")
    logger.info(f"  - {recipes_list_file.name}")
    logger.info(f"  - {items_ts_file.name}")
    logger.info(f"  - {recipes_ts_file.name}")
    logger.info(f"  - {benefits_ts_file.name}")


def main():
    """Main entry point."""
    try:
        logger.info("=" * 60)
        logger.info("Eco Data Reader - Python Version")
        logger.info("=" * 60)

        # Get user choice
        choice = get_user_choice()

        if choice == '3':
            logger.info("\nExiting without generating files.")
            return 0

        generate_all = (choice == '1')

        # Generate output files
        generate_output_files(generate_all)

    except FileNotFoundError as e:
        logger.error(f"\nConfiguration error: {e}")
        logger.error("\nPlease ensure:")
        logger.error("1. config.ini exists in the root directory")
        logger.error("2. ECO_SERVER_PATH is set to your Eco server Mods\\__core__ folder")
        return 1
    except Exception as e:
        logger.error(f"\nAn error occurred: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
