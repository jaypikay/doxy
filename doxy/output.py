from typing import List

from click import Context, echo
from rich import print
from rich.rule import Rule
from rich.tree import Tree


def _print_services_fancy(services: List, status: str):
    print(Rule("Listing services"))
    tree = Tree(f"[bold]{status.capitalize()} Services")
    for service in services:
        if isinstance(service, tuple):
            compose, subservices = service
            node = tree.add(compose)
            for subservice in subservices:
                node.add(subservice)
        else:
            tree.add(service)
    print(tree)


def _print_services_simple(services: List[str], status: str):
    for service in services:
        if isinstance(service, tuple):
            compose, subservices = service
            echo(f"{compose}\t{','.join(subservices)} ({status})")
        else:
            echo(service)


def print_services(ctx: Context, services: List[str], disabled_services=False):
    if not disabled_services:
        status = "enabled"
    else:
        status = "disabled"
    match ctx.obj["FORMAT"]:
        case "fancy":
            _print_services_fancy(services, status)
        case "simple":
            _print_services_simple(services, status)
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
