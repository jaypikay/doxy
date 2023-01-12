from dataclasses import dataclass
from pathlib import Path

from click import get_app_dir
from yamldataclassconfig import create_file_path_field
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class Config(YamlDataClassConfig):
    root_directory: str = ""
    compose_executable: str = ""

    FILE_PATH: Path = create_file_path_field(Path(get_app_dir("doxy")) / "config.yml")
