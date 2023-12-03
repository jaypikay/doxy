import sys
from pathlib import Path

import click
from click_aliases import ClickAliasedGroup

from doxy import output
from doxy.config import Config
from doxy.services import (
    disable_compose_file,
    docker_compose_command,
    enable_compose_file,
    find_disabled_services,
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
        for k in find_services(Path(CONFIG.root_directory), False)
        + find_disabled_services(Path(CONFIG.root_directory), False)
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
@click.option(
    "--service-root",
    "-r",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=Path(CONFIG.root_directory),
    help="Service root directory",
    show_default=True,
)
@click.pass_context
def main(ctx, format, service_root):
    ctx.ensure_object(dict)
    CONFIG.root_directory = service_root
    ctx.obj["CONFIG"] = CONFIG
    ctx.obj["FORMAT"] = format.lower()


@main.command(
    name="get-service-directory", help="get the service root directory", aliases=["dir"]
)
@click.pass_context
def change_dir(ctx):
    click.echo(ctx.obj["CONFIG"].root_directory)


@main.command(help="list available services", aliases=["l", "ls"])
@click.option(
    "--sub-services",
    "-s",
    is_flag=True,
    default=False,
    help="list sub services from compose file",
)
@click.pass_context
def list(ctx, sub_services):
    output.print_services(ctx, find_services(Path(CONFIG.root_directory), sub_services))
    output.print_services(
        ctx, find_disabled_services(Path(CONFIG.root_directory), sub_services), True
    )


@main.command(help="edit the compose file")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
@only_if_service_exists
def edit(ctx, service):
    output.print_header(ctx, f"Editing {service}")
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    click.edit(filename=str(compose_file))


@main.command(help="disable service")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.option(
    "--now",
    "-n",
    is_flag=True,
    default=False,
    help="shutdown service prior being disabled",
)
@click.pass_context
@only_if_service_exists
def disable(ctx, service, now):
    output.print_header(ctx, f"Disable {service}")
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    if now:
        docker_compose_command(["down", "--remove-orphans"], compose_file)
    disable_compose_file(Path(CONFIG.root_directory) / service)


@main.command(help="enable service")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.option(
    "--now",
    "-n",
    is_flag=True,
    default=False,
    help="shutdown service prior being disabled",
)
@click.pass_context
@only_if_service_exists
def enable(ctx, service, now):
    output.print_header(ctx, f"Disable {service}")
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    enable_compose_file(Path(CONFIG.root_directory) / service)
    if now:
        docker_compose_command(["up", "-d"], compose_file)


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


@main.command("start-all", help="start all services")
@click.pass_context
def start_all(ctx):
    for service in find_services(Path(CONFIG.root_directory), False):
        output.print_header(ctx, f"Starting {service}")
        compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
        docker_compose_command(["up", "-d"], compose_file)


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
    command_chain = [
        (f"Pulling {service} images", ["pull"]),
        (f"Starting {service}", ["up", "-d"]),
    ]
    if remove:
        command_chain.insert(0, (f"Stopping {service}", ["down", "--remove-orphans"]))
    for title, command in command_chain:
        output.print_header(ctx, title)
        docker_compose_command(command, compose_file)


@main.command(
    help="show service status (images, ps, top, logs)", aliases=["stat", "info"]
)
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.option(
    "--tail",
    type=str,
    default=10,
    show_default=True,
    help="Number of lines to show from the end of the logs",
)
@click.pass_context
@only_if_service_exists
def status(ctx, service, tail):
    compose_file = get_compose_file(Path(CONFIG.root_directory) / service)
    command_chain = [
        ("Images", ["images"]),
        ("Containers", ["ps"]),
        ("Running processes", ["top"]),
        ("Log Messages", ["logs", "--tail", tail]),
    ]
    for title, command in command_chain:
        output.print_header(ctx, title)
        docker_compose_command(command, compose_file)
