from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger
from api import validate
from functions import commands
import json
import core


@docs(
    tags=["Commands"],
    summary="Создание сессии для клиента",
    description="Создание уникальной сессии для клиента, которая будет учитывать уникальные настройки пользователя.",
    responses={
        200: {"description": "Сессия успешно создана"},
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
@validate.validate(validate.Create_session)
async def create_session(request: web.Request, parsed: validate.Create_session) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id

        commands.create_ai(user_id, parsed.paths)
        return web.Response(status=200)
    except Exception as e:
        logger.error("command_processing error: ", e)
        return web.Response(status=500, text=str(e))


@docs(
    tags=["Commands"],
    summary="Обработка текста и превращение в команду",
    description="Обработка текста и превращение в ответ и заданный алгоритм действий.",
    responses={
        200: {"description": "Указания для скрипта успешно выданы"},
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
@validate.validate(validate.Command_processing)
async def сommand_processing(request: web.Request, parsed: validate.Command_processing) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id

        res = await commands.command_processing(user_id, parsed.text_ru, parsed.text_en, parsed.save_cache)
        if not res:
            print("Нейросеть не смогла обработать запрос.", res)
            return web.Response(status=500, text="Нейросеть не смогла обработать запрос.")
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("command_processing error: ", e)
        return web.Response(status=500, text=str(e))


@docs(
    tags=["Commands"],
    summary="Очистить кэш",
    description="Очистить кэш.",
    responses={
        200: {"description": "Кэш очищен"},
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
async def clear_cache(request: web.Request) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id

        res = await commands.clear_cache(user_id)
        return web.json_response(res, status=200)
    except Exception as e:
        logger.error("command_processing error: ", e)
        return web.Response(status=500, text=str(e))
