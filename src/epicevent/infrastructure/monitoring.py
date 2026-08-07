import sentry_sdk

from epicevent.config.settings import settings


def init_monitoring() -> None:
    """Initializes Sentry SDK with configuration from settings."""
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            send_default_pii=True,
        )


def capture_exception(exception: Exception) -> None:
    """Captures an exception and ensures pending events are sent before exit."""
    sentry_sdk.capture_exception(exception)
    sentry_sdk.flush()
