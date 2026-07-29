import math

from epicevent.cli.console import ask


def handle_pagination(
    offset: int,
    limit: int,
    received_count: int,
    total_count: int,
) -> int | None:
    options = []
    if offset > 0:
        options.append("[P] Précédent")
    if offset + received_count < total_count:
        options.append("[N] Suivant")

    options.append("[Q] Quitter")

    menu = " | ".join(options)
    total_pages = math.ceil(total_count / limit)
    prompt = f"page {offset // limit + 1} / {total_pages} | {menu}"

    choice = ask(prompt, type=str).upper()

    if choice == "Q":
        return None
    elif choice == "N":
        return offset + limit if offset + received_count < total_count else offset
    elif choice == "P":
        return max(0, offset - limit)

    return offset
