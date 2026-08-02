"""Per-user locks must be stable per telegram_id and independent across users."""

import asyncio

from core.infrastructure.telegram.user_locks import get_user_lock


def test_same_user_gets_the_same_lock_instance() -> None:
    assert get_user_lock(111) is get_user_lock(111)


def test_different_users_get_different_locks() -> None:
    assert get_user_lock(111) is not get_user_lock(222)


async def test_lock_actually_excludes_concurrent_acquisition() -> None:
    lock = get_user_lock(333)
    assert not lock.locked()

    async with lock:
        assert lock.locked()
        # A second acquisition attempt must not succeed immediately.
        second_acquired = False

        async def try_acquire() -> None:
            nonlocal second_acquired
            async with lock:
                second_acquired = True

        task = asyncio.create_task(try_acquire())
        await asyncio.sleep(0)  # let the task run up to the blocking acquire
        assert not second_acquired

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    assert not lock.locked()
