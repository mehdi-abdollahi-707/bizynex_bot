"""HTTP adapters for the bot: the Telegram webhook and the health-check endpoint.

Business/conversation logic never lives here — this module's only job is
translating between Django's HTTP layer and aiogram's `Dispatcher`.
"""

from __future__ import annotations

import json

import structlog
from aiogram.types import Update
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pydantic import ValidationError

from core.infrastructure.telegram.bot_factory import get_bot, get_dispatcher

logger = structlog.get_logger("bizynex")


# No cookies/session involved — Telegram authenticates via the secret-token
# header checked below, not a browser-origin check, so Django's cookie-based
# CSRF protection doesn't apply to this server-to-server endpoint.
@csrf_exempt
@require_POST
async def telegram_webhook(request: HttpRequest) -> HttpResponse:
    """Receive a Telegram update and hand it to the aiogram dispatcher.

    Always acknowledges with 2xx once the secret token and payload are
    valid, even if handling the update raised — Telegram retries non-2xx
    responses, and retrying a bug that will fail again just wastes cycles.
    Every failure mode is logged instead, and an unhandled exception from
    inside a handler is additionally shown to the customer as a friendly
    message by `apps.bot.handlers.error_handler` — this view's own
    try/except is a second, coarser safety net around the whole dispatch
    call, not the customer-facing one.
    """
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != settings.WEBHOOK_SECRET:
        logger.warning("webhook.rejected_bad_secret")
        return HttpResponse(status=403)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        logger.warning("webhook.invalid_json")
        return HttpResponse(status=400)

    try:
        update = Update.model_validate(payload)
    except ValidationError:
        logger.warning("webhook.invalid_update_schema")
        return HttpResponse(status=400)

    logger.info("webhook.received", update_id=update.update_id)

    bot = get_bot()
    dispatcher = get_dispatcher()

    try:
        await dispatcher.feed_webhook_update(bot, update)
    except Exception:
        logger.exception("webhook.handler_error", update_id=update.update_id)

    return HttpResponse(status=200)


async def health_check(request: HttpRequest) -> JsonResponse:
    """Used by the keep-alive self-ping and by Render's own health probing."""
    return JsonResponse({"status": "ok"})
