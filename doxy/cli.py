import sys
from pathlib import Path

import click
from rich import print
from rich.rule import Rule
from rich.tree import Tree

from doxy import output, services
from doxy.config import Config

try:
    CONFIG = Config()
    CONFIG.load()
except FileNotFoundError as exc:
    click.echo(exc, sys.stderr)
    sys.exit(1)


def complete_service_name(ctx, param, incomplete):
    return [
        k
        for k in services.find_services(Path(CONFIG.root_directory))
        if k.startswith(incomplete)
    ]


@click.group()
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


@click.command(help="list available services")
@click.pass_context
def list(ctx):
    output.print_services(ctx, services.find_services(Path(CONFIG.root_directory)))


@click.command(help="edit the compose file")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
@services.only_if_service_exists
def edit(ctx, service):
    output.print_header(f"Editing {service}")
    compose_file = services.get_compose_file(
        Path(ctx.obj["CONFIG"].root_directory) / service
    )
    click.edit(filename=Path(compose_file))


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    ),
    help="run docker-compose commands",
)
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.argument("command", nargs=-1)
@click.pass_context
@services.only_if_service_exists
def control(ctx, service, command):
    output.print_header(f"Controlling {service}")
    compose_file = services.get_compose_file(
        Path(ctx.obj["CONFIG"].root_directory) / service
    )
    services.docker_compose_command(command, compose_file)


@click.command(help="pull the latest service images and restart")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.option(
    "--remove", "-r", is_flag=True, default=False, help="remove unused volumes"
)
@click.pass_context
@services.only_if_service_exists
def update(ctx, service, remove):
    compose_file = services.get_compose_file(
        Path(ctx.obj["CONFIG"].root_directory) / service
    )
    command_chain = {
        f"Stopping {service}": ["down" if remove else "stop"],
        f"Pulling {service} images": ["pull"],
        f"Starting {service}": ["up", "-d"],
    }
    for title, command in command_chain.items():
        output.print_header(ctx, title)
        services.docker_compose_command(command, compose_file)


@click.command(help="show service status (ps, top)")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
@services.only_if_service_exists
def status(ctx, service):
    compose_file = services.get_compose_file(
        Path(ctx.obj["CONFIG"].root_directory) / service
    )
    command_chain = {
        "Containers": ["ps"],
        "Running processes": ["top"],
    }
    for title, command in command_chain.items():
        output.print_header(ctx, title)
        services.docker_compose_command(command, compose_file)


main.add_command(list)
main.add_command(edit)
main.add_command(control)
main.add_command(update)
main.add_command(status)
