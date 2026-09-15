"""Conversion between JSON and the TypeScript const format used by EcoCraftingTool's output files."""

import re
import codecs
from typing import List


class JsonTypeScriptProcessor:
    """Converts between plain JSON and TypeScript with item/skill/craftingTable string refs
    swapped for the getXByNameID(...) lookup calls EcoCraftingTool expects."""

    @staticmethod
    def process_json_to_typescript(json_str: str) -> str:
        """Convert a JSON string to the TypeScript form used in generated output files."""
        result = json_str.replace('"', "'")
        result = re.sub(r"'item':\s*'(\w+)'", r"'item': getItemByNameID('\1')", result)
        result = re.sub(r"'skill':\s*'(\w+)'", r"'skill': getSkillByNameID('\1')", result)
        result = re.sub(r"'craftingTable':\s*'(\w+)'", r"'craftingTable': getCraftingTableByNameID('\1')", result)
        # Decode unicode escape sequences
        result = codecs.decode(result, 'unicode_escape')
        return result

    @staticmethod
    def process_typescript_to_json(typescript: str) -> str:
        """Convert the TypeScript form back to a plain JSON string (inverse of process_json_to_typescript)."""
        result = re.sub(r"'item':\s*getItemByNameID\('(\w+)'\)", r"'item':'\1'", typescript)
        result = re.sub(r"'skill':\s*getSkillByNameID\('(\w+)'\)", r"'skill':'\1'", result)
        result = re.sub(r"'craftingTable':\s*getCraftingTableByNameID\('(\w+)'\)", r"'craftingTable':'\1'", result)
        result = result.replace("'", '"')
        return result

    @staticmethod
    def wrap_module(imports: List[str], array_export_name: str, item_type: str,
                     array_ts: str, map_export_name: str, class_name: str,
                     map_lambda_var: str, header_comment: str = "") -> str:
        """Wrap a TypeScript array literal in the import/export/Map boilerplate EcoCraftingTool's
        data files expect (e.g. items.ts, recipes.ts, benefits.ts) - the array alone isn't
        importable since the Map lookups (and, for recipes, the getXByNameID resolution) live
        in that boilerplate, not the array literal itself."""
        import_block = "\n".join(imports)
        comment_block = f"\n{header_comment}" if header_comment else ""
        indented_array = "\n".join(f"  {line}" for line in array_ts.splitlines())
        return (
            f"{import_block}\n"
            f"{comment_block}\n"
            f"export const {array_export_name}: {item_type}[] =\n"
            f"{indented_array};\n"
            f"\n"
            f"export const {map_export_name}: Map<string, {class_name}> = new Map({array_export_name}.map(\n"
            f"  {map_lambda_var} => [{map_lambda_var}.nameID, new {class_name}({map_lambda_var})]\n"
            f"));\n"
        )
