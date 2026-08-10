from datetime import datetime

from rich.panel import Panel
from rich.table import Table

from epicevent.cli.console import (
    ask_required,
    ask_update_fields,
    console,
    display_message,
)
from epicevent.schemas.client_schema import (
    ClientDetailResponse,
    ClientResponse,
)


# helper
#################
def _ask_date(prompt: str) -> str:
    while True:
        value = ask_required(prompt)
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            display_message("Format invalide. Veuillez utiliser JJ/MM/AAAA", "warning")


# create_client
#################
def display_client_create_resume() -> None:
    display_message("Création d'un nouveau client", "info")


def ask_client_creation_data() -> dict:
    last_name = ask_required("Nom de famille")
    first_name = ask_required("Prénom")
    email = ask_required("Email")
    phone = ask_required("Numéro de téléphone")
    business_name = ask_required("Nom de l'entreprise")
    first_contact = _ask_date("Premier contact (JJ/MM/AAAA)")
    last_contact = _ask_date("Dernier contact (JJ/MM/AAAA)")
    return {
        "last_name": last_name,
        "first_name": first_name,
        "email": email,
        "phone": phone,
        "business_name": business_name,
        "first_contact": first_contact,
        "last_contact": last_contact,
    }


def display_client_creation_success(client: ClientResponse) -> None:
    display_message(
        f"Le client ({client.email}) a été enregistré.",
        "success",
    )


# update_client
#################
def display_client_update_resume(target_client: ClientResponse) -> None:
    display_message(
        f"Mis à jour du client {target_client.last_name} {target_client.first_name}",
        "info",
    )


def ask_client_update_data() -> dict:
    fields = {
        "1": ("first_name", "Prénom"),
        "2": ("last_name", "Nom"),
        "3": ("email", "Email"),
        "4": ("phone", "Téléphone"),
        "5": ("first_contact", "Date du premier contact"),
        "6": ("last_contact", "Date du dernier contact"),
    }

    return ask_update_fields(fields)


def display_client_update_success(client: ClientResponse) -> None:
    display_message(
        f"Le client ({client.email}) a été mis à jour.",
        "success",
    )


def display_client_update_cancel() -> None:
    display_message("La mise à jour du client a été annulée.", "info")


# list_clients
#################
def display_clients_table(
    clients_list: list[ClientDetailResponse],
    total_count: int,
) -> None:
    """
    Display clients in a formatted table.

    Args:
        clients_list: Clients to display.
        total_count: Total number of client matching the query.
    """
    table = Table(title=f"\nListe des clients ({total_count} au total)")
    table.add_column("Nom")
    table.add_column("Prénom")
    table.add_column("Email")
    table.add_column("Nom de l'entreprise")
    table.add_column("Contact commercial")

    for client in clients_list:
        sales_representative_info = (
            f"{client.sales_representative.first_name} "
            f"{client.sales_representative.last_name} "
            f"(n°{client.sales_representative.employee_number})"
        )
        table.add_row(
            client.last_name,
            client.first_name,
            client.email,
            client.business_name,
            sales_representative_info,
        )

    console.print(table)


def display_clients_list_empty_message() -> None:
    display_message("Aucun client trouvé", "warning")


# show_client
######################
def display_client_details(client: ClientDetailResponse) -> None:
    table = Table(show_header=False, box=None)

    table.add_column(style="highlight")

    first_contact = client.first_contact.strftime("%d/%m/%Y")
    last_contact = client.last_contact.strftime("%d/%m/%Y")
    sales_representative_info = (
        f"{client.sales_representative.first_name} "
        f"{client.sales_representative.last_name} "
        f"(n°{client.sales_representative.employee_number})"
    )

    table.add_row("Nom complet:", f"{client.first_name} {client.last_name}")
    table.add_row("Email", client.email)
    table.add_row("Téléphone:", client.phone)
    table.add_row("Nom de l'entreprise: ", client.business_name)
    table.add_row("Premier contact:", first_contact)
    table.add_row("Dernier contact", last_contact)
    table.add_row("Contact commercial", sales_representative_info)

    console.print(
        "",
        Panel(
            table,
            expand=False,
            title=f"[italic]Client {client.email}[/italic]",
        ),
    )
