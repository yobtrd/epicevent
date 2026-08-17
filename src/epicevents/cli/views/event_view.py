from datetime import datetime

import click
from rich.panel import Panel
from rich.table import Table

from epicevents.cli.console import (
    ask,
    ask_required,
    ask_update_fields,
    console,
    display_message,
)
from epicevents.schemas.contract_schema import ContractResponse
from epicevents.schemas.event_schema import EventDetailResponse, EventResponse
from epicevents.schemas.user_schema import UserResponse


# helpers
#####################
def _format_datetime(value: datetime) -> str:
    return value.strftime("%d/%m/%Y %H:%M")


def _ask_datetime(prompt: str) -> datetime:
    while True:
        value = ask_required(prompt)
        try:
            return datetime.strptime(value, "%d/%m/%Y %H:%M")
        except ValueError:
            display_message(
                "Format invalide. Veuillez utiliser JJ/MM/AAAA HH:MM", "warning"
            )


# create_event
#####################
def display_event_create_resume(target_contract: ContractResponse) -> None:
    display_message(
        f"Création d'un événement pour le contrat n°{target_contract.id} du client "
        f"{target_contract.client.last_name} {target_contract.client.first_name}"
    )


def ask_event_creation_data() -> dict:
    name = ask_required("Nom de l'événement")
    start = _ask_datetime("Date et heure de début (JJ/MM/AAAA HH:MM)")
    end = _ask_datetime("Date et heure de fin (JJ/MM/AAAA HH:MM)")
    location = ask_required("Lieu de l'événement")
    attendees = ask_required("Nombre de participants")
    notes = ask("Notes additionnelles (optionnel)", default="", show_default=False)

    notes = notes.strip() or None

    return {
        "name": name,
        "start": start,
        "end": end,
        "location": location,
        "attendees": attendees,
        "notes": notes,
    }


def display_event_creation_success(event: EventResponse) -> None:
    display_message(
        f'L\'événement "{event.name}" (n°{event.id}) a été enregistré.',
        "success",
    )


# update_event
#####################
def display_event_update_resume(target_event: EventResponse) -> None:
    display_message(
        f'Modification de l\'événement "{target_event.name}" '
        f"(n°{target_event.id}) du contrat "
        f"n°{target_event.contract_id}."
    )


def ask_event_update_data() -> dict:
    fields = {
        "1": ("name", "Nom de l'événement"),
        "2": ("start", "Date et heure de début"),
        "3": ("end", "Date et heure de fin"),
        "4": ("location", "Lieu de l'événement"),
        "5": ("attendees", "Nombre de participants"),
        "6": ("notes", "Notes additionnelles"),
    }

    return ask_update_fields(fields)


def display_event_update_success(event: EventResponse) -> None:
    display_message(
        f'L\'événement "{event.name}" (n°{event.id}) a bien été mis à jour.'
    )


def display_event_update_cancel() -> None:
    display_message("La mise à jour de l'événement a été annulée.", "info")


# list_events
#####################
def display_events_table(
    events_list: list[EventDetailResponse],
    total_count: int,
) -> None:
    """
    Display events in a formatted table.

    Args:
        events_list: Events to display.
        total_count: Total number of event matching the query.
    """
    table = Table(title=f"\nListe des événements ({total_count} au total)")
    table.add_column("Nom")
    table.add_column("Id de l'événement")
    table.add_column("Id du contrat")
    table.add_column("Nom du client")
    table.add_column("Date et heure de début")
    table.add_column("Contact support")
    table.add_column("Lieu de l'événement")

    for event in events_list:
        client = f"{event.contract.client.last_name} {event.contract.client.first_name}"

        support_contact = (
            f"{event.support_representative.first_name} "
            f"{event.support_representative.last_name} "
            f"(n°{event.support_representative.employee_number})"
            if event.support_representative
            else "Non assigné"
        )

        table.add_row(
            event.name,
            str(event.id),
            str(event.contract.id),
            client,
            _format_datetime(event.start),
            support_contact,
            event.location,
        )

    console.print(table)


def display_events_list_empty_message() -> None:
    display_message("Aucun événement trouvé", "warning")


# show_contract
######################
def display_event_details(event: EventDetailResponse) -> None:
    table = Table(show_header=False, box=None)

    table.add_column(style="highlight")

    client = (
        f"{event.contract.client.first_name} "
        f"{event.contract.client.last_name} "
        f"({event.contract.client.email})"
    )
    sales_contact = (
        f"{event.contract.sales_representative.first_name} "
        f"{event.contract.sales_representative.last_name} "
        f"(n°{event.contract.sales_representative.employee_number})"
    )
    support_contact = (
        f"{event.support_representative.first_name} "
        f"{event.support_representative.last_name} "
        f"(n°{event.support_representative.employee_number})"
        if event.support_representative
        else "Non assigné"
    )

    table.add_row("Nom:", event.name)
    table.add_row("Id de l'événement:", str(event.id))
    table.add_row("Id du contrat:", str(event.contract.id))
    table.add_row("Client:", client)
    table.add_row("Contact du client:", sales_contact)
    table.add_row("Date et heure de début:", _format_datetime(event.start))
    table.add_row("Date et heure de fin:", _format_datetime(event.end))
    table.add_row("Contact du support:", support_contact)
    table.add_row("Lieu de l'événement:", event.location)
    table.add_row("Nombre de participants:", str(event.attendees))
    table.add_row("Notes additionnelles:", event.notes or "")

    console.print(
        "",
        Panel(
            table,
            expand=False,
            title=f"[italic]Événement n°{event.id}[/italic]",
        ),
    )


# assign_support
#####################
def ask_assign_support_confirmation(
    target_event: EventResponse,
    target_support: UserResponse,
) -> bool:
    display_message(
        f"Vous aller assigner {target_support.last_name} "
        f"{target_support.first_name} (n°{target_support.employee_number}) "
        f"à l'événement {target_event.name} (n°{target_event.id})",
        "info",
    )
    return click.confirm("Confirmer ? ([Y] pour confirmer, [N] pour annuler)")


def display_assign_support_success(
    assigned_support: UserResponse,
    updated_event: EventResponse,
) -> None:
    display_message(
        f"Le collaborateur {assigned_support.last_name} "
        f"{assigned_support.first_name} "
        f"(n°{assigned_support.employee_number}) "
        "a bien été assigné comme support à l'événement "
        f"n°{updated_event.id}",
        "success",
    )


def display_assign_support_cancel() -> None:
    display_message("L'ajout du collaborateur support a été annulée.", "info")


# unassign_support
#####################
def ask_unassign_support_confirmation(target_event: EventDetailResponse) -> bool:
    display_message(
        f"Désassigner le support {target_event.support_representative.last_name} "
        f"{target_event.support_representative.first_name} de l'événement"
        f'"{target_event.name}" n°{target_event.id} ?'
    )
    return click.confirm("[Y] pour confirmer, [N] pour annuler")


def display_unassign_support_success(updated_event: EventDetailResponse) -> None:
    display_message(
        f"Le support a bien été désassigner de l'événement n°{updated_event.id}", "info"
    )


def display_unassign_support_cancel() -> None:
    display_message("La désassignation du collaborateur support a été annulée.", "info")
