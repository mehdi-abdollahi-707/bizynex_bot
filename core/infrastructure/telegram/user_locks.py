"""Per-user in-process locks, guarding against double-submission races —
e.g. a fast double-tap on "✅ ثبت درخواست" before the first tap's DB write
and button update have taken effect, which could otherwise create two
`ProjectRequest` rows (and send the admin two notifications) for one
submission.

In-memory only, which is correct here because this bot always runs as a
single worker process (see render.yaml / Procfile) — there's exactly one
event loop these locks need to coordinate within.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict

_locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)


def get_user_lock(telegram_id: int) -> asyncio.Lock:
    return _locks[telegram_id]
