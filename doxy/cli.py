import sys
from pathlib import Path

import click
from rich import print
from rich.rule import Rule
from rich.tree import Tree

from doxy import services
from doxy.config import Config

try:
    CONFIG = Config()
    CONFIG.load()
except FileNotFoundError as exc:
    click.echo(exc, sys.stderr)
    sys.exit(1)


@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)
    ctx.obj["CONFIG"] = CONFIG


@click.command(help="list available services")
def list():
    print(Rule(f"Listing services"))
    tree = Tree("[bold]Available Services")
    for service in services.find_services(Path(CONFIG.root_directory)):
        tree.add(service)
    print(tree)


def complete_service_name(ctx, param, incomplete):
    return [
        k
        for k in services.find_services(Path(CONFIG.root_directory))
        if k.startswith(incomplete)
    ]


@click.command(help="edit the compose file")
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
@services.only_if_service_exists
def edit(ctx, service):
    print(Rule(f"Editing {service}"))
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
    print(Rule(f"Controlling {service}"))
    compose_file = services.get_compose_file(
        Path(ctx.obj["CONFIG"].root_directory) / service
    )
    services.docker_compose_command(command, compose_file)


@click.command("update", help="pull the latest service images and restart")
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
    print(Rule(f"Updating {service}"))
    services.docker_compose_command(
        [
            ["stop", "down"][remove],
        ],
        compose_file,
    )
    services.docker_compose_command(
        [
            "pull",
        ],
        compose_file,
    )
    services.docker_compose_command(["up", "-d"], compose_file)


main.add_command(list)
main.add_command(edit)
main.add_command(control)
main.add_command(update)
