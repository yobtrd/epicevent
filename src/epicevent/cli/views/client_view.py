from datetime import datetime

from epicevent.cli.console import ask, ask_required, console, display_message
from epicevent.schemas.client_schema import ClientResponse


# Helpers
#################
def _ask_date(prompt: str) -> str:
    while True:
        value = ask_required(prompt)
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            display_message("Format invalide. Veuillez utiliser JJ/MM/AAAA", "warning")


# create
#################
def ask_client_creation_data() -> dict:
    last_name = ask_required("Nom")
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


def display_creation_success(client_response: ClientResponse):
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

    updates = {}
    while True:
        console.print("\nChoisissez le champ à modifier :", style="highlight")
        for key, (_, label) in fields.items():
            console.print(f"{key}. {label}")
        console.print("q. Terminer la saisie")

        choice = ask("Votre choix").strip()
        if choice.lower() == "q":
            break

        if choice in fields:
            attr, label = fields[choice]
            value = ask(f"\nNouveau {label.lower()}")

            if value:
                updates[attr] = value
        else:
            console.print("Choix invalide", style="warning")
    return updates


def display_update_cancel():
    display_message("La mise à jour du client a été annulée", "info")


def display_update_success(client: ClientResponse):
    display_message(
        f"Le client ({client.email}) a été mis à jour.",
        "success",
    )
