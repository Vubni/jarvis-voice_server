import os
from aiohttp import web
from aiohttp_apispec import (
    setup_aiohttp_apispec,
    validation_middleware
)
import aiohttp_cors
from config import logger
import asyncio
from api import (auth, profile, commands)
from database.functions import init_db

if __name__ == "__main__":
    asyncio.run(init_db())

    app = web.Application()

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE"]
        )
    })

    setup_aiohttp_apispec(
        app,
        title="API doc",
        version="v1",
        url="/swagger.json",
        swagger_path="/doc",
        security_definitions={
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Bearer token authorization"
            }
        }
    )

    prefix = "/"
    routes = [
        web.post(prefix + 'auth/register', auth.register),
        web.post(prefix + 'auth/auth', auth.auth),
        web.post(prefix + 'auth/forgot_password', auth.forgot_password),
        web.get(prefix + 'auth/forgot_password/confirm',
                auth.forgot_password_confirm),

        web.get(prefix + 'profile/info', profile.get),
        # web.get(prefix + 'profile/subscription', profile.subscription),
        web.post(prefix + 'profile/check_token', profile.check_token),
        # web.post(prefix + 'profile/url_renew_subscripe', profile.renew_subscripe),

        web.post(prefix + 'commands/create_session', commands.create_session),
        web.post(prefix + 'commands/command_processing',
                 commands.сommand_processing),
        web.post(prefix + 'commands/clear_cache', commands.clear_cache),
        # web.get('/{path:.*}', handle_get_file)
    ]

    for route in routes:
        cors.add(app.router.add_route(route.method, route.path, route.handler))

    app.middlewares.append(validation_middleware)

    logger.info("Запуск сервера. . .")
    web.run_app(
        app,
        host=os.environ.get('INSTANCE_HOST', 'localhost'),
        port=int(os.environ.get('PORT', 8080))
    )
