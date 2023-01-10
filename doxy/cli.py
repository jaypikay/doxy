import click
from pathlib import Path

from rich import print
from rich.tree import Tree

from doxy.config import Config
from doxy import services


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


@click.command()
@click.pass_context
@click.argument("service", nargs=1)
@click.argument("command", nargs=-1)
def control(ctx, service, command):
    compose_file = services.get_compose_file(Path(ctx.obj["CONFIG"].root_directory) / service)
    services.docker_compose_command(command, compose_file)


main.add_command(list)
main.add_command(control)
