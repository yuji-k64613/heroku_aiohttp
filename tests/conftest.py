import sys
import os
import gc
import pytest
import asyncio
import psycopg2
from aiopg import sa


sys.path.append(
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
)
import modules.db as db


@pytest.fixture
def loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def get_engine(loop):
    engine = None

    async def go():
        nonlocal engine

        dsn = os.environ["DATABASE_URL"]
        engine = await sa.create_engine(dsn)
        return engine

    yield go

    if engine is not None:
        engine.close()
        loop.run_until_complete(engine.wait_closed())


@pytest.fixture(autouse=True)
async def test_insert(get_engine):
    tbl = db.get_tbl()
    dele = tbl.delete()
    ins = tbl.insert()
    engine = await get_engine()
    async with engine.acquire() as conn:
        async with conn.begin():
            await conn.execute(dele)
            await conn.execute(ins, {"id": 1, "name": "foo", "password": "bar"})
