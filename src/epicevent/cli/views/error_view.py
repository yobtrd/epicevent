from epicevent.cli.console import console
from epicevent.exception import (
    ApplicationError,
    AuthenticationError,
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
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
    }

    messages = {
        "Email": 'Format invalide, une adresse email doit contenir un "@".',
        "Mot de passe": "Format invalide, le mot de passe doit contenir "
        "au moins 8 caractères.",
    }

    for err in error.errors:
        raw_field = err["loc"][-1]
        label = labels.get(raw_field, raw_field)
        message = messages.get(label, "Saisie invalide.")

        console.print(f"\n{label}: {message}\n", style="warning")
