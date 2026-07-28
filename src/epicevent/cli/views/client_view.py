from datetime import datetime

from epicevent.cli.console import ask_required, display_message
from epicevent.schemas.client_schema import ClientResponse


# Helpers
###############
def _ask_date(prompt: str) -> str:
    while True:
        value = ask_required(prompt)
        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            display_message("Format invalide. Veuillez utiliser JJ/MM/AAAA", "warning")


# create
###############
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
