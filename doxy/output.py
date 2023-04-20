from typing import List

from click import Context, echo
from rich import print
from rich.rule import Rule
from rich.tree import Tree


def _print_services_fancy(services: List):
    print(Rule("Listing services"))
    tree = Tree("[bold]Available Services")
    for service in services:
        if isinstance(service, tuple):
            compose, subservices = service
            node = tree.add(compose)
            for subservice in subservices:
                node.add(subservice)
        else:
            tree.add(service)
    print(tree)


def _print_services_simple(services: List[str]):
    for service in services:
        if isinstance(service, tuple):
            compose, subservices = service
            echo(f"{compose}\t{','.join(subservices)}")
        else:
            echo(service)


def print_services(ctx: Context, services: List[str]):
    match ctx.obj["FORMAT"]:
        case "fancy":
            _print_services_fancy(services)
        case "simple":
            _print_services_simple(services)
        case _:
            echo("Unknown format choice")


def _print_header_fancy(text: str):
    print(Rule(text))


def print_header(ctx: Context, text: str):
    match ctx.obj["FORMAT"]:
        case "fancy":
            _print_header_fancy(text)
        case _:
            pass
