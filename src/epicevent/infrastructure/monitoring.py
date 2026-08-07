import sentry_sdk

from epicevent.config import SENTRY_DSN


def init_monitoring() -> None:
    """Initializes Sentry SDK with configuration from settings."""
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            send_default_pii=True,
            debug=False,
        )


def capture_exception(exception: Exception) -> None:
    """Captures an exception and ensures pending events are sent before exit."""
    sentry_sdk.capture_exception(exception)
    sentry_sdk.flush()
