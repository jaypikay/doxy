import sys
from pathlib import Path

import click
from click_aliases import ClickAliasedGroup

from doxy import output
from doxy.config import Config
from doxy.services import (
    docker_compose_command,
    find_services,
    get_compose_file,
    only_if_service_exists,
)

try:
    CONFIG = Config()
    CONFIG.load()
except FileNotFoundError as exc:
    click.echo(exc, sys.stderr)
    sys.exit(1)


def complete_service_name(ctx, param, incomplete):
    return [
        k
        for k in find_services(Path(CONFIG.root_directory))
        if k.startswith(incomplete)
    ]


@click.group(cls=ClickAliasedGroup)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["fancy", "simple"], case_sensitive=False),
    default="fancy",
    show_default=True,
    help="output formatting",
)
@click.pass_context
def main(ctx, format):
    ctx.ensure_object(dict)
    ctx.obj["CONFIG"] = CONFIG
    ctx.obj["FORMAT"] = format.lower()


@main.command(help="list available services", aliases=["l", "ls"])
@click.pass_context
def list(ctx):
    output.print_services(ctx, find_services(Path(CONFIG.root_directory)))


@main.command(help="edit the compose file")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
@only_if_service_exists
def edit(ctx, service):
    output.print_header(ctx, f"Editing {service}")
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    click.edit(filename=Path(compose_file))


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
    ),
    help="run docker-compose commands",
    aliases=["c", "ctrl"],
)
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.argument("command", nargs=-1)
@click.pass_context
@only_if_service_exists
def control(ctx, service, command):
    output.print_header(ctx, f"Controlling {service}")
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    docker_compose_command(command, compose_file)


@main.command(
    help="pull the latest service images and restart", aliases=["upd", "sync"]
)
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.option(
    "--remove", "-r", is_flag=True, default=False, help="remove unused volumes"
)
@click.pass_context
@only_if_service_exists
def update(ctx, service, remove):
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    command_chain = {
        f"Stopping {service}": ["down" if remove else "stop"],
        f"Pulling {service} images": ["pull"],
        f"Starting {service}": ["up", "-d"],
    }
    for title, command in command_chain.items():
        output.print_header(ctx, title)
        docker_compose_command(command, compose_file)


@main.command(help="show service status (ps, top)", aliases=["stat", "info"])
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
@only_if_service_exists
def status(ctx, service):
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    command_chain = {
        "Containers": ["ps"],
        "Running processes": ["top"],
    }
    for title, command in command_chain.items():
        output.print_header(ctx, title)
        docker_compose_command(command, compose_file)
