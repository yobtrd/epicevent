import click
from rich.table import Table

from epicevent.cli.console import (
    ask_required,
    ask_update_fields,
    console,
    display_message,
)
from epicevent.schemas.client_schema import ClientResponse
from epicevent.schemas.contract_schema import ContractDetailResponse, ContractResponse


# create_contract
####################
def display_contract_create_resume(target_client: ClientResponse) -> None:
    display_message(
        f"Création d'un contrat pour le client {target_client.last_name} "
        f"{target_client.first_name}",
        "info",
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


def display_contract_creation_success(contract: ContractResponse) -> None:
    display_message(f"Le contrat n°{contract.id} a été enregistré.", "success")


# update_contract
####################
def display_contract_update_resume(target_contract: ContractResponse) -> None:
    display_message(
        f"Modification du contrat n°{target_contract.id} du client "
        f"{target_contract.client.last_name} {target_contract.client.first_name}.",
        "info",
    )


def ask_contract_update_data() -> dict:
    fields = {
        "1": ("total_amount", "Montant total du contrat"),
        "2": ("remaining_amount", "Montant restant du contrat"),
        "3": ("is_signed", "Statut du contrat ([Y] Signé | [N] Non signé"),
    }

    return ask_update_fields(fields)


def display_contract_update_success(contract: ContractResponse) -> None:
    display_message(f"Le contrat n°{contract.id} a été mis à jour.", "success")


def display_contract_update_cancel() -> None:
    display_message("La mise à jour du contrat a été annulée.", "info")


# list_contracts
####################
def display_contracts_table(
    contracts_list: list[ContractDetailResponse],
    total_count: int,
) -> None:
    """
    Display contracts in a formatted table.

    Args:
        contracts_list: Contracts to display.
        total_count: Total number of contracts matching the query.
    """
    table = Table(title=f"\nListe des contrats ({total_count} au total)")
    table.add_column("Id du contrat")
    table.add_column("Client")
    table.add_column("Contact commercial du client")
    table.add_column("Montant total")
    table.add_column("Montant restant")
    table.add_column("Créé le")
    table.add_column("Statut")

    for contract in contracts_list:
        client = (
            f"{contract.client.last_name} {contract.client.first_name} "
            f"({contract.client.email})"
        )
        sales_representative = (
            f"{contract.sales_representative.last_name} "
            f"{contract.sales_representative.first_name} "
            f"(n°{contract.sales_representative.employee_number})"
        )
        created_at = contract.created_at.strftime("%d/%m/%Y %H:%M")
        statut = "Signé" if contract.is_signed is True else "Non signé"

        table.add_row(
            str(contract.id),
            client,
            sales_representative,
            str(contract.total_amount),
            str(contract.remaining_amount),
            created_at,
            statut,
        )

    console.print(table)


def display_contract_list_empty_message() -> None:
    display_message("Aucun contrat trouvé", "warning")
