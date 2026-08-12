import click

from epicevent.cli import error_handler
from epicevent.cli.commands.auth_cli import auth
from epicevent.cli.commands.client_cli import client
from epicevent.cli.commands.contract_cli import contract
from epicevent.cli.commands.event_cli import event
from epicevent.cli.commands.user_cli import user
from epicevent.exception import ConfigurationError
from epicevent.infrastructure import monitoring


@click.group()
def cli():
    """Epicevent CLI."""


def main():
    """
    Entry point of the application.

    Initializes monitoring and handles configuration errors and unexpected
    application errors. Unexpected errors are reported to Sentry.
    """
    try:
        monitoring.init_monitoring()
        cli()
    except ConfigurationError as error:
        error_handler.display_configuration_error(error)
    except Exception as error:
        monitoring.capture_exception(error)
        error_handler.display_unexpected_error()
    finally:
        monitoring.shutdown_monitoring()


cli.add_command(auth)
cli.add_command(user)
cli.add_command(client)
cli.add_command(contract)
cli.add_command(event)
