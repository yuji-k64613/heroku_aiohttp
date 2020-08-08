import os
import logging
from aiohttp import web
import modules.server as server
import modules.settings as settings

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    config = settings.get_config()
    app['config'] = config

    server.setup_routes(app)
    app.on_startup.append(server.init_pg)
    app.on_cleanup.append(server.close_pg)

    port = int(config.get("server").get("port"))
    port = int(os.environ.get('PORT', port))
    web.run_app(app, host="0.0.0.0", port=port)
