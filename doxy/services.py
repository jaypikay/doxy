import glob
import subprocess
import sys
from functools import update_wrapper
from pathlib import Path
from typing import List

import click
import yaml


def only_if_service_exists(fn):
    def wrapper(*args, **kwargs):
        ctx = args[0]
        service = kwargs["service"]
        try:
            compose_file = get_compose_file(
                Path(ctx.obj["CONFIG"].root_directory) / service
            )
            if not compose_file.exists():
                raise FileNotFoundError()
        except FileNotFoundError:
            click.echo(f"Service `{service}' not found", sys.stderr)
            ctx.abort()
        return ctx.invoke(fn, *args, **kwargs)

    return update_wrapper(wrapper, fn)


def load_docker_compose(compose_file: Path) -> dict:
    with open(compose_file) as fd:
        compose_yaml = yaml.safe_load(fd.read())
    return compose_yaml


def find_services(root: Path, sub_services: bool) -> List:
    if not sub_services:
        services = [
            _.split("/")[0] for _ in glob.glob("*/docker-compose.y*ml", root_dir=root)
        ]
    else:
        services = []
        for compose_file in glob.glob("*/docker-compose.y*ml", root_dir=root):
            services.append(
                (compose_file.split("/")[0], get_subservices(root / compose_file))
            )
    return services


def find_disabled_services(root: Path, sub_services: bool) -> List:
    if not sub_services:
        services = [
            _.split("/")[0]
            for _ in glob.glob("*/docker-compose.y*ml.disabled", root_dir=root)
        ]
    else:
        services = []
        for compose_file in glob.glob("*/docker-compose.y*ml.disabled", root_dir=root):
            services.append(
                (compose_file.split("/")[0], get_subservices(root / compose_file))
            )
    return services


def disable_compose_file(service_path: Path):
    target_path = Path(service_path / "docker-compose.yml.disabled")
    compose_file = get_compose_file(service_path)
    compose_file.rename(target_path)


def enable_compose_file(service_path: Path):
    target_path = Path(service_path / "docker-compose.yml")
    compose_file = get_compose_file(service_path)
    compose_file.rename(target_path)


def get_compose_file(service_path: Path) -> Path:
    compose_files = glob.glob("docker-compose.y*ml", root_dir=service_path)
    if len(compose_files) == 0:
        compose_files = glob.glob("docker-compose.y*ml.disabled", root_dir=service_path)
    try:
        return service_path / compose_files[0]
    except IndexError:
        raise FileNotFoundError


def get_subservices(compose_file: Path) -> List[str]:
    compose_yaml = load_docker_compose(compose_file)
    return compose_yaml["services"].keys()


def docker_compose_command(commands: List[str], compose_file: Path):
    ctx = click.get_current_context()
    config = ctx.obj["CONFIG"]
    cmd = config.compose_executable.split() + ["-f", compose_file] + list(commands)
    subprocess.run(cmd)
