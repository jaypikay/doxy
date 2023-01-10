from xdg import xdg_config_home
from pathlib import Path
from dataclasses import dataclass

from yamldataclassconfig import create_file_path_field
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class Config(YamlDataClassConfig):
    root_directory: str = None
    compose_executable: str = None

    FILE_PATH: Path = create_file_path_field(Path(xdg_config_home()) / "doxy/config.yml")
