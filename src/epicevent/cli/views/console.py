import click
from rich.console import Console
from rich.theme import Theme

theme = Theme(
    {
        "error": "bold red",
        "warning": "bold yellow",
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


def ask_required(label: str, **kwargs):
    while True:
        value = ask(label, default="", show_default=False, **kwargs)
        if value.strip():
            return value.strip()
        console.print("Ce champ est obligatoire.", style="warning")
