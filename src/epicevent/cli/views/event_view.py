from datetime import datetime

from rich.table import Table

from epicevent.cli.console import (
    ask,
    ask_datetime,
    ask_required,
    console,
    display_message,
)
from epicevent.schemas.contract_schema import ContractResponse
from epicevent.schemas.event_schema import EventResponse


# helpers
#################
def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "N/A"


# create
#################
def display_event_create_resume(target_contract: ContractResponse):
    display_message(
        f"Création d'un évenement pour le contrat n° {target_contract.id} du client "
        f" {target_contract.client.last_name} {target_contract.client.first_name}"
    )


def ask_event_creation_data() -> dict:
    start = ask_datetime("Date et heure de début (JJ/MM/AAAA HH:MM)")
    end = ask_datetime("Date et heure de fin (JJ/MM/AAAA HH:MM)")
    location = ask_required("Lieu de l'événement")
    attendees = ask_required("Nombre de participants")
    notes = ask("Notes additionnelles (optionnel)", default="", show_default=False)

    notes = None if notes == "" else notes
    return {
        "start": start,
        "end": end,
        "location": location,
        "attendees": attendees,
        "notes": notes,
    }


def display_event_creation_success(event: EventResponse):
    display_message(
        f"L'évenement (id: {event.id}) a été enregistré.",
        "success",
    )


# list
#################
def display_events_table(events_list: list[EventResponse], total_count: int):
    table = Table(title=f"\nListe des évènements ({total_count} au total)")
    table.add_column("Id de l'évènement")
    table.add_column("Id du contrat")
    table.add_column("Nom du client")
    table.add_column("Contact du client")
    table.add_column("Date et heure de début")
    table.add_column("Date et heure de fin")
    table.add_column("Contact du support")
    table.add_column("Lieu de l'événement")
    table.add_column("Nombre de participants")
    table.add_column("Notes additionnelles")

    for event in events_list:
        client = f"{event.contract.client.last_name} {event.contract.client.first_name}"
        sales_representative = (
            f"{event.contract.sales_representative.last_name} "
            f"{event.contract.sales_representative.first_name} "
            f"(n°{event.contract.sales_representative.employee_number})"
        )
        if event.support_representative:
            support_representative = (
                f"{event.support_representative.last_name} "
                f"{event.support_representative.first_name} "
                f"n°{event.support_representative.employee_number}"
            )
        else:
            support_representative = "Aucun support associé pour le moment."

        table.add_row(
            str(event.id),
            str(event.contract.id),
            client,
            sales_representative,
            format_datetime(event.start),
            format_datetime(event.end),
            support_representative,
            event.location,
            str(event.attendees),
            event.notes,
        )

    console.print(table)


def display_events_list_empty_message():
    display_message("Aucun événement trouvé", "warning")
