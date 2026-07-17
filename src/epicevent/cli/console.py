import click
from rich.console import Console
from rich.theme import Theme

theme = Theme(
    {
        "error": "red",
        "warning": "yellow",
        "success": "green",
        "info": "blue",
    }
)

console = Console(theme=theme)


def ask(label: str, **kwargs):
    return click.prompt(
        click.style(label, fg="white", bold=True),
        **kwargs,
    )
