from epicevent.cli.console import console
from epicevent.exception import (
    ApplicationError,
    AuthenticationError,
    ClientNotFoundError,
    ClientOwnershipError,
    ContractNotFoundError,
    ContractNotSignedError,
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
    EventNotFoundError,
    EventOwnershipError,
    InvalidCredentialsError,
    InvalidInputError,
    RolePermissionError,
    UserAlreadyDeactivatedError,
    UserNotFoundError,
)

ERROR_MESSAGES = {
    AuthenticationError: "Vous n'êtes pas connecté à une session.",
    RolePermissionError: "Vous n'avez pas les droits pour cette action.",
    InvalidCredentialsError: "Email ou mot de passe incorrect, veuillez réessayer.",
    UserNotFoundError: "L'utilisateur n'a pas été trouvé.",
    EmailAlreadyExistsError: "Cet email existe déjà.",
    UserAlreadyDeactivatedError: "Cet utilisateur est déjà désactivé",
    EmployeeNumberAlreadyExistsError: "Ce numéro d'employé existe déjà.",
    ClientNotFoundError: "Le client n'a pas été trouvé.",
    ClientOwnershipError: "Vous n'avez pas la gestion de ce client.",
    ContractNotFoundError: "Le contrat n'a pas été trouvé.",
    ContractNotSignedError: "Le contrat n'a pas encore été signé.",
    EventNotFoundError: "L'évènement n'a pas été trouvé.",
    EventOwnershipError: "Vous n'avez pas la gestion de cet évènement.",
}


def display_application_error(error: ApplicationError):
    message = ERROR_MESSAGES.get(type(error))

    if message:
        console.print(f"\nErreur: {message}\n", style="error")
    else:
        console.print("\nErreur: Une erreur inattendue est survenue.\n", style="error")


def display_invalid_input_error(error: InvalidInputError):
    labels = {
        "email": "Email",
        "password": "Mot de passe",
        "employee_number": "Numéro d'employé",
        "total_amount": "Montant",
        "remaining_amount": "Montant",
        "attendees": "Nombre de participant",
    }

    messages = {
        "Email": 'Format invalide, une adresse email doit contenir un "@".',
        "Mot de passe": "Format invalide, le mot de passe doit contenir "
        "au moins 8 caractères.",
        "Montant": "Format invalide, Le montant doit être un nombre entier ou décimal "
        "(ex: 1000 ou 1000.50).",
        "Nombre de participant": " Format invalide, Le nombre doit être un nombre "
        "entier sans espaces (ex: 500) et ne peut dépasser 1000000.",
    }

    for err in error.errors:
        raw_field = err["loc"][-1]
        label = labels.get(raw_field, raw_field)
        message = messages.get(label, "Saisie invalide.")

        console.print(f"\n{label}: {message}\n", style="warning")
