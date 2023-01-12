import sys
from pathlib import Path

import click
from rich import print
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


@click.command()
@click.pass_context
def list(ctx):
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


@click.command()
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
def edit(ctx, service):
    try:
        compose_file = services.get_compose_file(
            Path(ctx.obj["CONFIG"].root_directory) / service
        )
        click.edit(filename=Path(compose_file))
    except FileNotFoundError:
        click.echo(f"Service `{service}' not found", sys.stderr)
        ctx.abort()


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.argument("command", nargs=-1)
@click.pass_context
def control(ctx, service, command):
    try:
        compose_file = services.get_compose_file(
            Path(ctx.obj["CONFIG"].root_directory) / service
        )
        services.docker_compose_command(command, compose_file)
    except FileNotFoundError:
        click.echo(f"Service `{service}' not found", sys.stderr)
        ctx.abort()


main.add_command(list)
main.add_command(edit)
main.add_command(control)
