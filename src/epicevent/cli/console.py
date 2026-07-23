import click
from rich.console import Console
from rich.theme import Theme

theme = Theme(
    {
        "error": "bold red",
        "warning": "yellow",
        "success": "bold green",
        "info": "blue",
        "highlight": "bold white",
    }
)

console = Console(
    theme=theme,
    highlight=False,
    markup=False,
)


def ask(label: str, **kwargs):
    return click.prompt(
        click.style(label, fg="white", bold=True),
        **kwargs,
    )
