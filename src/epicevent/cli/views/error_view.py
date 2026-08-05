from epicevent.cli.console import display_message
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
    InvalidContactDatesError,
    InvalidContractAmountError,
    InvalidCredentialsError,
    InvalidEventDatesError,
    InvalidInputError,
    RolePermissionError,
    SuperuserAlreadyExistsError,
    SupportAssignmentError,
    UserAlreadyDeactivatedError,
    UserDisabledError,
    UserNotFoundError,
)

ERROR_MESSAGES = {
    SuperuserAlreadyExistsError: "Un superuser a déjà été créé.",
    AuthenticationError: "Vous n'êtes pas connecté à une session.",
    RolePermissionError: "Vous n'avez pas les droits pour cette action.",
    InvalidCredentialsError: "Email ou mot de passe incorrect, veuillez réessayer.",
    UserDisabledError: "Compte désactivé, veuillez contacter un administrateur.",
    UserNotFoundError: "L'utilisateur n'a pas été trouvé.",
    EmailAlreadyExistsError: "Cet email existe déjà.",
    UserAlreadyDeactivatedError: "Cet utilisateur est déjà désactivé.",
    EmployeeNumberAlreadyExistsError: "Ce numéro d'employé existe déjà.",
    ClientNotFoundError: "Le client n'a pas été trouvé.",
    ClientOwnershipError: "Vous n'avez pas la gestion de ce client.",
    InvalidContactDatesError: "La date du dernier contact ne peut être antérieure "
    "au premier contact.",
    ContractNotFoundError: "Le contrat n'a pas été trouvé.",
    ContractNotSignedError: "Le contrat n'a pas encore été signé.",
    InvalidContractAmountError: "Le montant restant ne peut être inférieure "
    "au montant total.",
    EventNotFoundError: "L'événement n'a pas été trouvé.",
    EventOwnershipError: "Vous n'avez pas la gestion de cet événement.",
    InvalidEventDatesError: "La date de fin de l'événement ne peut être antérieure "
    "à sa date de début",
    SupportAssignmentError: "L'utilisateur assigné n'est pas du département support.",
}

INVALID_INPUT_LABELS = {
    "email": "Email",
    "password": "Mot de passe",
    "employee_number": "Numéro d'employé",
    "total_amount": "Montant",
    "remaining_amount": "Montant",
    "attendees": "Nombre de participant",
}

INVALID_INPUT_MESSAGES = {
    "Email": 'une adresse email doit contenir un "@".',
    "Mot de passe": "le mot de passe doit contenir au moins 8 caractères.",
    "Montant": "le montant doit être un nombre entier ou décimal "
    "supérieur ou égal à 0 (ex: 1000 ou 1000.50).",
    "Nombre de participant": "le nombre doit être un nombre entier sans "
    "espaces (ex: 500) et ne peut dépasser 1000000.",
}


def display_application_error(error: ApplicationError) -> None:
    """
    Display an application error message.

    Args:
        error: Application exception raised by the application layer.
    """
    message = ERROR_MESSAGES.get(type(error))

    if message:
        display_message(f"Erreur: {message}", "error")
    else:
        display_message("Erreur: Une erreur inattendue est survenue.", "error")


def display_invalid_input_error(error: InvalidInputError) -> None:
    """
    Display validation errors returned by input schemas.

    Args:
        error: Validation exception containing invalid fields.
    """
    for err in error.errors:
        raw_field = err.get("loc")[-1]

        label = INVALID_INPUT_LABELS.get(raw_field, raw_field)

        error_type = err.get("type")
        if error_type == "string_too_long":
            limit = err.get("ctx", {}).get("max_length", "X")
            display_message(
                f"{label}: est trop long (maximum {limit} caractères)", "warning"
            )
            continue

        message = INVALID_INPUT_MESSAGES.get(label, "Saisie invalide.")
        display_message(f"{label}: Format invalide, {message}", "warning")
