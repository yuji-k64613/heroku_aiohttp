import os
import re
import logging

import asyncio
import aiohttp
from aiohttp import web
from aiopg.sa import create_engine

import modules.settings as setting
import modules.db as db
import modules.utils as utils

config = setting.get_config()
engine = None


async def fetch(session, url):
    async with session.get(url) as response:
        ct = response.headers["Content-Type"]
        logging.info(f"Content-Type={ct}")
        if utils.is_text(ct):
            text = await response.text()
            binary = None
        else:
            text = None
            binary = await response.read()
        await response.release()
        return text, binary, response


def acquire():
    global engine

    return engine.acquire()


async def main(request):
    # HTTPパラメータ
    query = request.query

    # cookie
    cookies = request.cookies
    auth = False

    if "logout" in query:
        return None, None, None, None

    # URL
    host = config.get("server").get("host")
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
        #async with engine.acquire() as conn:
        async with acquire() as conn:
            user = await db.get_user(conn, param_user, param_password)
        if user is None:
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
    headers = {k: headers[k] for k in headers.keys()}
    del headers["Host"]

    # HTTPリクエスト
    async with aiohttp.ClientSession(headers=headers) as session:
        text, binary, response = await fetch(session, url)
    await session.close()

    return text, binary, auth, response


async def handle(request):
    logging.info(f"START {str(request.url)}")
    text, binary, auth, response = await main(request)

    if response is None:
        text = "logout"
        resp = web.Response(text=text)
        resp.del_cookie("auth")
    elif text is not None:
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
    app.router.add_get(r"/{path:.*}", handle)


async def init_pg(app):
    global environ
    global engine

    dsn = os.environ["DATABASE_URL"]
    engine = await create_engine(dsn)
    app["db"] = engine


async def close_pg(app):
    app["db"].close()
    await app["db"].wait_closed()
