import click

from epicevent.cli.console import ask_required, display_message
from epicevent.schemas.contract_schema import ContractResponse

# create
#################


def display_contract_create_resume(target_client):
    display_message(
        f"Création d'un contrat pour le client {target_client.last_name} "
        f"{target_client.first_name}"
    )


def ask_contract_creation_data() -> dict:
    total_amount = ask_required("Montant total du contrat")
    remaining_amount = ask_required("Montant restant")
    is_signed = click.confirm("Le contrat est-il signé ? ([Y] Oui | [N] Non)")

    return {
        "total_amount": total_amount,
        "remaining_amount": remaining_amount,
        "is_signed": is_signed,
    }


def display_creation_success(contract_response: ContractResponse):
    display_message(
        f"Le contrat (id: {contract_response.id}) a été enregistré.",
        "success",
    )
