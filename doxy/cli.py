from pathlib import Path

import click
from rich import print
from rich.tree import Tree

from doxy import services
from doxy.config import Config


@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)
    config = Config()
    config.load()
    ctx.obj["CONFIG"] = config


@click.command()
@click.pass_context
def list(ctx):
    tree = Tree("[bold]Available Services")
    for service in services.find_services(Path(ctx.obj["CONFIG"].root_directory)):
        tree.add(service)
    print(tree)


def complete_service_name(ctx, param, incomplete):
    config = Config()
    config.load()
    return [
        k
        for k in services.find_services(Path(config.root_directory))
        if k.startswith(incomplete)
    ]


@click.command()
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.pass_context
def edit(ctx, service):
    compose_file = services.get_compose_file(
        Path(ctx.obj["CONFIG"].root_directory) / service
    )
    click.edit(filename=Path(compose_file))


@click.command()
@click.pass_context
@click.argument("service", nargs=1, shell_complete=complete_service_name)
@click.argument("command", nargs=-1)
def control(ctx, service, command):
    compose_file = services.get_compose_file(
        Path(ctx.obj["CONFIG"].root_directory) / service
    )
    services.docker_compose_command(command, compose_file)


main.add_command(list)
main.add_command(edit)
main.add_command(control)
