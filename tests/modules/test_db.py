import pytest
import asyncio
import modules.db as db

@pytest.mark.asyncio
async def test_get_user(get_engine):
    user = "foo"

    engine = await get_engine()
    async with engine.acquire() as conn:
        user = await db.get_user(conn, user)

    assert user is not None
