import glob
from typing import List
from pathlib import Path
import subprocess


def find_services(root: Path) -> List[str]:
    return [_.split("/")[0] for _ in glob.glob("*/docker-compose.y*ml", root_dir=root)]


def get_compose_file(service_path: Path) -> Path:
    compose_files = glob.glob("docker-compose.y*ml", root_dir=service_path)
    try:
        return service_path / compose_files[0]
    except IndexError:
        raise FileNotFoundError


def docker_compose_command(commands: List[str], compose_file: Path): 
    cmd = ["docker-compose", "-f", compose_file] + list(commands)
    subprocess.run(cmd)
