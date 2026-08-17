import click

from epicevents.cli import error_handler
from epicevents.cli.commands.auth_cli import auth
from epicevents.cli.commands.client_cli import client
from epicevents.cli.commands.contract_cli import contract
from epicevents.cli.commands.event_cli import event
from epicevents.cli.commands.user_cli import user
from epicevents.exception import ConfigurationError
from epicevents.infrastructure import monitoring


@click.group()
def cli():
    """epicevents CLI."""


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
