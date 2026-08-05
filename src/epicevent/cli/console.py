from datetime import datetime

import click
from rich.console import Console
from rich.theme import Theme

theme = Theme(
    {
        "error": "bold red",
        "warning": "bold yellow",
        "success": "bold green",
        "info": "bold blue",
        "highlight": "bold white",
    }
)

console = Console(
    theme=theme,
    highlight=False,
    markup=False,
)


def display_message(message: str, style: str = "info"):
    console.print(f"\n{message}\n", style=style)


def ask(label: str, **kwargs):
    value = click.prompt(
        click.style(label, fg="white", bold=True),
        **kwargs,
    )
    return value.strip()


def ask_required(label: str, **kwargs):
    while True:
        value = ask(label, default="", show_default=False, **kwargs)
        if value.strip():
            return value.strip()
        console.print("Ce champ est obligatoire.", style="warning")


def ask_update_fields(fields: dict[str, tuple[str, str]]) -> dict:
    updates = {}

    while True:
        console.print("\nChoisissez le champ à modifier :", style="highlight")

        for key, (_, label) in fields.items():
            console.print(f"{key}. {label}")

        console.print("q. Terminer la saisie")

        choice = ask("Votre choix")

        if choice.lower() == "q":
            break

        if choice in fields:
            attr, label = fields[choice]
            value = ask(f"\nNouveau/velle {label.lower()}")

            if value:
                updates[attr] = value
        else:
            console.print("Choix invalide", style="warning")

    return updates


def ask_date(prompt: str) -> str:
    while True:
        value = ask_required(prompt)
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            display_message("Format invalide. Veuillez utiliser JJ/MM/AAAA", "warning")


def ask_datetime(prompt: str) -> datetime:
    while True:
        value = ask_required(prompt)
        try:
            return datetime.strptime(value, "%d/%m/%Y %H:%M")
        except ValueError:
            display_message(
                "Format invalide. Veuillez utiliser JJ/MM/AAAA HH:MM", "warning"
            )
