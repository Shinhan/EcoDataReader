import configparser
import os
from pathlib import Path


class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to config.ini in the root directory
            root_dir = Path(__file__).parent.parent
            config_path = root_dir / "config.ini"

        self.config_path = config_path
        self.config = configparser.ConfigParser()

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Config file not found at {config_path}. "
                f"Copy config.ini.example to config.ini and set your ECO_SERVER_PATH."
            )

        self.config.read(config_path)

    @property
    def eco_server_path(self) -> str:
        path = self.config.get('Paths', 'ECO_SERVER_PATH', fallback='')
        if not path:
            raise ValueError(
                "ECO_SERVER_PATH is not set in config.ini. "
                "Please set the path to your Eco server Mods\\__core__ folder."
            )
        return path

    @property
    def eco_crafting_tool_path(self) -> str:
        return self.config.get('Paths', 'ECO_CRAFTING_TOOL_PATH', fallback='')

    @property
    def white_tiger_path(self) -> str:
        return self.config.get('Paths', 'WHITE_TIGER_PATH', fallback='')
