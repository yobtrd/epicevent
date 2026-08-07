import click

from epicevent.cli.commands.auth_cli import auth
from epicevent.cli.commands.client_cli import client
from epicevent.cli.commands.contract_cli import contract
from epicevent.cli.commands.event_cli import event
from epicevent.cli.commands.user_cli import user
from epicevent.cli.error_handler import display_unexpected_error
from epicevent.infrastructure.monitoring import capture_exception, init_monitoring


@click.group()
def cli():
    """Epicevent CLI."""


def main():
    init_monitoring()
    try:
        cli()
    except Exception as error:
        capture_exception(error)
        display_unexpected_error()


cli.add_command(auth)
cli.add_command(user)
cli.add_command(client)
cli.add_command(contract)
cli.add_command(event)
