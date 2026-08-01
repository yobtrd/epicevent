from rich.table import Table

from epicevent.cli.console import (
    ask_date,
    ask_required,
    ask_update_fields,
    console,
    display_message,
)
from epicevent.schemas.client_schema import ClientDetailResponse, ClientResponse


# create
#################
def ask_client_creation_data() -> dict:
    last_name = ask_required("Nom")
    first_name = ask_required("Prénom")
    email = ask_required("Email")
    phone = ask_required("Numéro de téléphone")
    business_name = ask_required("Nom de l'entreprise")
    first_contact = ask_date("Premier contact (JJ/MM/AAAA)")
    last_contact = ask_date("Dernier contact (JJ/MM/AAAA)")
    return {
        "last_name": last_name,
        "first_name": first_name,
        "email": email,
        "phone": phone,
        "business_name": business_name,
        "first_contact": first_contact,
        "last_contact": last_contact,
    }


def display_client_creation_success(client_response: ClientResponse):
    display_message(
        f"Le client (email: {client_response.email}) a été enregistré.",
        "success",
    )


# update_client
#################
def display_user_update_resume(target_client: ClientResponse):
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
        "7": ("address", "Adresse"),
    }

    return ask_update_fields(fields)


def display_update_cancel():
    display_message("La mise à jour du client a été annulée", "info")


def display_update_success(client: ClientResponse):
    display_message(
        f"Le client ({client.email}) a été mis à jour.",
        "success",
    )


# list
#################
def display_clients_table(clients_list: list[ClientDetailResponse], total_count: int):
    table = Table(title=f"\nListe des clients ({total_count} au total)")
    table.add_column("Nom")
    table.add_column("Prénom")
    table.add_column("Email")
    table.add_column("Téléphone")
    table.add_column("Nom de l'entreprise")
    table.add_column("Premier contact")
    table.add_column("Dernier Contact")
    table.add_column("Contact commercial")

    for client in clients_list:
        first_contact = (
            client.first_contact.strftime("%d/%m/%Y") if client.first_contact else "-"
        )
        last_contact = (
            client.last_contact.strftime("%d/%m/%Y") if client.last_contact else "-"
        )
        sales_representative_info = (
            f"{client.sales_representative.first_name} "
            f"{client.sales_representative.last_name} "
            f"(n°{client.sales_representative.employee_number})"
        )
        table.add_row(
            client.last_name,
            client.first_name,
            client.email,
            client.phone,
            client.business_name,
            first_contact,
            last_contact,
            sales_representative_info,
        )

    console.print(table)


def display_clients_list_empty_message():
    display_message("Aucun client trouvé", "warning")
