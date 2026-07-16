import click

from .commands.auth_cli import auth


@click.group()
def cli():
    """Epicevent CLI"""


cli.add_command(auth)
