import glob
import subprocess
from pathlib import Path
from typing import List

import click


def find_services(root: Path) -> List[str]:
    return [_.split("/")[0] for _ in glob.glob("*/docker-compose.y*ml", root_dir=root)]


def get_compose_file(service_path: Path) -> Path:
    compose_files = glob.glob("docker-compose.y*ml", root_dir=service_path)
    try:
        return service_path / compose_files[0]
    except IndexError:
        raise FileNotFoundError


def docker_compose_command(commands: List[str], compose_file: Path):
    ctx = click.get_current_context()
    config = ctx.obj["CONFIG"]
    cmd = [config.compose_executable, "-f", compose_file] + list(commands)
    subprocess.run(cmd)
