import pytest
import asyncio
from aiohttp import web
import modules.server as server

@pytest.mark.asyncio
async def test_setup_routes(aiohttp_client, loop, mocker):
    res = web.Response(text="Hello, world right!")
    mocker.patch('modules.server.handle', return_value=res)

    app = web.Application()
    app.router.add_get(r"/{path:.*}", server.handle)

    client = await aiohttp_client(app)
    
    resp = await client.get("/?user=foo&password=bar")
    assert resp.status == 200
    text = await resp.text()
    assert "Hello, world" in text

@pytest.mark.asyncio
async def test_handle(aiohttp_client, loop, mocker):
    text = "Hello, world right!"
    res = web.Response(text=text)
    mocker.patch('modules.server.main', return_value=(text, None, None, res))

    app = web.Application()
    app.router.add_get(r"/{path:.*}", server.handle)

    client = await aiohttp_client(app)

    resp = await client.get("/?user=foo&password=bar")
    assert resp.status == 200
    text = await resp.text()
    assert "Hello, world" in text
