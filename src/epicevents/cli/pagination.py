import math

from epicevents.cli.console import ask


def handle_pagination(
    offset: int,
    limit: int,
    received_count: int,
    total_count: int,
) -> int | None:
    """
    Display pagination options and return the next offset.

    Args:
        offset: Current pagination offset.
        limit: Number of items requested per page.
        received_count: Number of items returned on the current page.
        total_count: Total number of available items.

    Returns:
        The next offset to fetch, or None when pagination should stop.
    """
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
    if choice == "N":
        return offset + limit if offset + received_count < total_count else offset
    if choice == "P":
        return max(0, offset - limit)

    return offset
