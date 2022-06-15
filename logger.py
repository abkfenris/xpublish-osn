import logging
import os

from settings import settings

if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn, traces_sample_rate=settings.sentry_sample_rate
    )

logger = logging.getLogger("uvicorn")
