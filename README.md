# Eco Data Reader

A Python tool for reading and processing Eco server game data. Extracts items, recipes, skills, and crafting tables from Eco server files and generates TypeScript-formatted output for use with tools like the [EcoCraftingTool](https://github.com/aritchie05/EcoCraftingTool).

## Initial Setup

### Prerequisites

- Python 3.7 or later (or just downloaded [embeddable Python](https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip) into your root directory
- Eco server files (Can be read directly from your game directory)

### Installation

1. **Clone or download this repository**
2. **Configure the application**
   Copy `config.ini.example` to `config.ini` and set your `ECO_SERVER_PATH` to your Eco server's `Mods\__core__` folder:
   ```ini
   ECO_SERVER_PATH = D:\Eco Servers\EcoServerPC_v0.10.0.0-beta\Mods\__core__
   ```
   `config.ini` is gitignored, so your local paths won't be committed.

3. **Run the application**
   - Windows: Double-click `run.bat`
   - Linux/Mac: `./run.sh` or `python main.py`

4. **Choose what to generate**
   - Option 1: All items and recipes (complete dataset)
   - Option 2: Only NEW items (not in reference files)
   - Option 3: Exit

## Output Files

Generated files are saved to the `output/` folder:

- **all-items.txt** - List of all item names
- **all-items.ts** - TypeScript export of all items
- **all-recipes.txt** - List of all recipe names
- **all-recipes.ts** - TypeScript export of all recipes

## Usage

### Generate All Data

```bash
python main.py
# Select option 1
```

### Generate Only New Items

```bash
python main.py
# Select option 2
```

This compares against reference files in `src/main/resources/` to identify new items/recipes.

## License

MIT License - See LICENSE file for details

## Credits

- [EcoDataReader](https://github.com/aritchie05/EcoDataReader)

## Related

- [EcoCraftingTool](https://github.com/aritchie05/EcoCraftingTool) - Web-based crafting calculator for Eco
- [Eco Game](https://play.eco) - The game this tool supports
