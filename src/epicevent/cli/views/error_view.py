from enum import Enum

from epicevent.cli.console import console
from epicevent.exception import InvalidInputError


class ErrorMessage(Enum):
    NOT_AUTHENTICATED = "Vous n'êtes pas connecté à une session."
    NOT_AUTHORIZED = "Vous n'avez pas les droits pour cette action."
    USER_NOT_FOUND = "L'utilisateur n'a pas été trouvé."
    EMAIL_ALREADY_EXISTS = "Cet email existe déjà."
    EMPLOYEE_NUMBER_ALREADY_EXISTS = "Ce numéro d'employé existe déjà."
    UNKNOWN = "Une erreur inattendue est survenue."


def display_error(message: ErrorMessage):
    console.print(f"[error]Erreur: {message.value}[/error]")


def display_invalid_input_error(error: InvalidInputError):
    messages = {
        (
            "email",
            "value_error",
        ): 'Format invalide, une adresse email doit contenir un "@".'
    }
    for err in error.errors:
        field = ".".join(err["loc"])
        message = messages.get((field, err["type"]), "Valeur invalide.")

        console.print(f"[error]Erreur sur le champ {field}: {message}[/error]")
