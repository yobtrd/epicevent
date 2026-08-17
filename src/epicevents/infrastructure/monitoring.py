import sentry_sdk

from epicevents.config.settings import get_settings


def init_monitoring() -> None:
    """Initializes Sentry SDK with configuration from settings."""
    settings = get_settings()
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            send_default_pii=True,
        )


def capture_exception(exception: Exception) -> None:
    """Captures an exception with Sentry."""
    sentry_sdk.capture_exception(exception)


def capture_event(event_name: str, **data: object) -> None:
    """Capture a business event in Sentry."""
    with sentry_sdk.new_scope() as scope:
        for key, value in data.items():
            scope.set_extra(key, value)

        sentry_sdk.capture_message(event_name)


def shutdown_monitoring():
    sentry_sdk.flush()
