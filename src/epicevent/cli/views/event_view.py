from epicevent.cli.console import ask, ask_datetime, ask_required, display_message
from epicevent.schemas.contract_schema import ContractResponse
from epicevent.schemas.event_schema import EventResponse


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
