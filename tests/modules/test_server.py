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


class DummyConn(object): 
    def __init__(self): 
        pass
      
    #def __enter__(self): 
    #    return None
  
    #def __exit__(self): 
    #    pass

    async def __aenter__(self): 
        return None
    
    async def __aexit__(self, exc_type, exc, tb): 
        pass


@pytest.mark.asyncio
async def test_main(aiohttp_client, loop, mocker):
    dummy = DummyConn()
    mocker.patch('modules.server.acquire', return_value=dummy)

    from collections import namedtuple
    User = namedtuple('User', ['user', 'password'])
    user = User(user="foo", password="bar")
    mocker.patch('modules.db.get_user', return_value=user)

    text = "Hello, world right!"
    res = web.Response(text=text)
    mocker.patch('modules.server.fetch', return_value=(text, None, res))

    app = web.Application()
    app.router.add_get(r"/{path:.*}", server.handle)

    client = await aiohttp_client(app)

    resp = await client.get("/?user=foo&password=bar")
    assert resp.status == 200
    text = await resp.text()
    assert "Hello, world" in text
