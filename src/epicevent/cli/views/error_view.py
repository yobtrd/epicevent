from epicevent.cli.console import console
from epicevent.exception import (
    ApplicationError,
    AuthenticationError,
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
    InvalidCredentialsError,
    InvalidInputError,
    RolePermissionError,
    UserNotFoundError,
)

ERROR_MESSAGES = {
    AuthenticationError: "Vous n'êtes pas connecté à une session.",
    RolePermissionError: "Vous n'avez pas les droits pour cette action.",
    InvalidCredentialsError: "Email ou mot de passe incorrect, veuillez réessayer.",
    UserNotFoundError: "L'utilisateur n'a pas été trouvé.",
    EmailAlreadyExistsError: "Cet email existe déjà.",
    EmployeeNumberAlreadyExistsError: "Ce numéro d'employé existe déjà.",
}


def display_application_error(error: ApplicationError):
    message = ERROR_MESSAGES.get(type(error))

    if message:
        console.print(f"Erreur: {message}", style="error")
    else:
        console.print("Erreur: Une erreur inattendue est survenue.", style="error")


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

        console.print(f"Erreur sur le champ {field}: {message}", style="error")
