"""Self-ping task that keeps Render's free-tier instance from sleeping.

Render's free web services sleep after ~15 minutes with no inbound HTTP
traffic. Outbound calls this process makes (e.g. to Telegram's API) don't
reset that timer — only a real inbound request to this service's own port
does. So this task periodically issues an HTTP GET against our own
`/health/` endpoint from inside the same running process.
"""

from __future__ import annotations

import asyncio

import aiohttp
import structlog

logger = structlog.get_logger("bizynex")


async def run_keepalive_loop(*, url: str, interval_seconds: int) -> None:
    """Ping `url` forever, every `interval_seconds`. Runs as a background task."""
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(interval_seconds)
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    logger.info("keepalive.ping", status=response.status)
            except Exception as exc:  # noqa: BLE001 - a failed ping must never kill the loop
                logger.warning("keepalive.ping_failed", error=str(exc))
