import os
import re
import logging

import asyncio
import aiohttp
from aiohttp import web
from aiopg.sa import create_engine
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, TIMESTAMP

app = web.Application()
logging.basicConfig(level=logging.INFO)

# テーブル定義
metadata = sa.MetaData()
tbl = sa.Table(
    'users', metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), unique=True),
    Column("password", String(120), unique=True),
)

async def fetch(session, url):
    async with session.get(url) as response:
        ct = response.headers["Content-Type"]
        logging.info(f"Content-Type={ct}")
        if re.match("^text/", ct):
            text = await response.text()
            binary = None
        else:
            text = None
            binary = await response.read()
        await response.release()
        return text, binary, response

async def main(request):
    # HTTPパラメータ
    query = request.query

    # cookie
    cookies = request.cookies;
    auth = False

    if "logout" in query:
        return None, None, None, None 

    # URL
    host = "python.org"
    path = request.path
    url = f"http://{host}{path}"
    
    if "auth" in cookies:
        logging.info("Authenticated")
    else:
        param_user = ""
        param_password = ""
        if not "user" in query or not "password" in query:
            logging.error("ERROR1!!")
            raise web.HTTPUnauthorized()
        else:
            param_user = request.query["user"]
            param_password = request.query["password"]
    
        # DBアクセス(認証)
        engine = app['db']
        async with engine.acquire() as conn:
            query = sa.select([ tbl.c.id, tbl.c.name, tbl.c.password ]).select_from(tbl).where(tbl.c.name == param_user)
            user = await (await conn.execute(query)).first()
        if not user:
            logging.error("ERROR2!!")
            raise web.HTTPUnauthorized()
        elif user.password != param_password:
            logging.error("ERROR3!!")
            raise web.HTTPUnauthorized()
        else:
            logging.info(f"user = {user}")
            auth = True

    # リクエストヘッダ
    headers = request.headers
    headers = { k: headers[k] for k in headers.keys() }
    del headers["Host"]

    # HTTPリクエスト
    async with aiohttp.ClientSession(headers=headers) as session:
        text, binary, response = await fetch(session, url)
    await session.close()

    return text, binary, auth, response

async def handle(request):
    logging.info(f"START {str(request.url)}")
    text, binary, auth, response = await main(request)

    if not response:
        text = "logout"
        resp = web.Response(text=text)
        resp.del_cookie("auth")
    elif text:
        resp = web.Response(text=text)
    else:
        resp = web.StreamResponse()
        await resp.prepare(request)
        await resp.write(binary)

    if response:
        resp.content_type = response.headers["Content-Type"]
    if auth:
        resp.set_cookie("auth", "ok")

    logging.info(f"END {str(request.url)}")
    return resp

def setup_routes(app):
    app.router.add_get(r'/{path:.*}', handle)

async def init_pg(app):
    dsn = os.environ['DATABASE_URL']
    engine = await create_engine(dsn)
    app['db'] = engine

async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()

setup_routes(app)
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, host="0.0.0.0", port=port)
