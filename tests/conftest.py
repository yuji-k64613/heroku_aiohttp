import sys
import os

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../src/")
)

# import logging
# from aiohttp import web
# import modules.server as server
# import modules.settings as settings

# logging.basicConfig(level=logging.INFO)
# app = web.Application()
# config = settings.get_config()
# app["config"] = config

# server.setup_routes(app)
# app.on_startup.append(server.init_pg)
# app.on_cleanup.append(server.close_pg)

# port = int(config.get("server").get("port"))
# port = int(os.environ.get("PORT", port))
# web.run_app(app, host="0.0.0.0", port=port)

import pytest
import asyncio
import psycopg2
from aiopg import sa
import gc

# @pytest.fixture
# def loop(request):
#    loop = asyncio.new_event_loop()
#    asyncio.set_event_loop(None)
#
#    yield loop
#
#    if not loop._closed:
#        loop.call_soon(loop.stop)
#        loop.run_forever()
#        loop.close()
#    gc.collect()
#    asyncio.set_event_loop(None)

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


@pytest.fixture
def loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
