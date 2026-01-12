from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from api import validate
from functions import profile as func
import json
import core
from docs import schems as sh
from functions import mail


@docs(
    tags=["Profile"],
    summary="Получение профиля",
    description="Получить профиль.",
    responses={
        200: {"description": "Профиль успешно получен"},
        400: {"description": "Отсутствует один из параметров или ограничения параметра не выполнены"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    },
    parameters=[{
        'in': 'header',
        'name': 'Authorization',
        'schema': {'type': 'string', 'format': 'Bearer'},
        'required': True,
        'description': 'Bearer-токен для аутентификации'
    }]
)
async def get(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id

        await func.get(user_id)
        return web.Response(status=200)
    except Exception as e:
        logger.error("command_processing error: ", e)
        return web.Response(status=500, text=str(e))


@docs(
    tags=["Profile"],
    summary="Проверка активности токена",
    description="Проверка активности токена. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Токен активный."},
        400: {"description": "Токен авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Токен неактивный"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    },
    parameters=[{
        'in': 'header',
        'name': 'Authorization',
        'schema': {'type': 'string', 'format': 'Bearer'},
        'required': True,
        'description': 'Bearer-токен для аутентификации'
    }]
)
async def check_token(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        return web.Response(status=204)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))


@docs(
    tags=["Profile"],
    summary="Верификация email",
    description="Подтверждает почту. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        204: {"description": "Почта успешно подтверждена"},
        400: {"description": "Код авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Код подтверждения неверный"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    },
    parameters=[{
        'in': 'header',
        'name': 'Authorization',
        'schema': {'type': 'string', 'format': 'Bearer'},
        'required': True,
        'description': 'Bearer-токен для аутентификации'
    }]
)
async def email_verify(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id

        try:
            await func.verify_email(user_id)
            return web.Response(status=204)
        except:
            return web.Response(status=500)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))


@docs(
    tags=["Profile"],
    summary="Получение ссылки на подписку",
    description="Получение ссылки на подписку. Для доступа требуется Bearer-токен в заголовке Authorization",
    responses={
        200: {"description": "Получение ссылки на подписку", "schema": sh.UrlSchema},
        400: {"description": "Код авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Код подтверждения неверный"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    },
    parameters=[{
        'in': 'header',
        'name': 'Authorization',
        'schema': {'type': 'string', 'format': 'Bearer'},
        'required': True,
        'description': 'Bearer-токен для аутентификации'
    }]
)
async def subscripe(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id

        try:
            await func.subscripe(user_id)
            return web.Response(status=204)
        except:
            return web.Response(status=500)
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
