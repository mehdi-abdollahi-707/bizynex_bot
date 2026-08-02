"""Singleton `Bot` and `Dispatcher`, constructed once and reused across every
webhook request handled by this worker process.

`@lru_cache` gives us process-wide singletons without a manually-managed
module-level global — the first call builds the instance, every later call
in the same worker returns it.
"""

from __future__ import annotations

from functools import lru_cache

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.conf import settings

from core.infrastructure.telegram.fsm_storage import DjangoFSMStorage


@lru_cache
def get_bot() -> Bot:
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


@lru_cache
def get_dispatcher() -> Dispatcher:
    from apps.bot.handlers import (
        error_handler,
        estimator,
        fallback,
        navigation,
        request_form,
        start,
    )
    from apps.bot.middlewares.customer_identity import CustomerIdentityMiddleware

    dispatcher = Dispatcher(storage=DjangoFSMStorage())

    identity_middleware = CustomerIdentityMiddleware()
    dispatcher.message.outer_middleware(identity_middleware)
    dispatcher.callback_query.outer_middleware(identity_middleware)

    # Registering error_handler's `errors()` hook on any included router
    # catches unhandled exceptions from every router in the dispatcher —
    # verified empirically, since aiogram propagates handler exceptions to
    # the dispatcher-level error observer regardless of origin. Order
    # relative to the other routers doesn't matter for this reason.
    dispatcher.include_router(error_handler.router)

    dispatcher.include_router(start.router)
    dispatcher.include_router(navigation.router)
    dispatcher.include_router(estimator.router)
    dispatcher.include_router(request_form.router)
    # fallback.router is included last so it only ever catches genuinely
    # unrecognized input, never something a more specific router above
    # would have handled.
    dispatcher.include_router(fallback.router)

    return dispatcher
