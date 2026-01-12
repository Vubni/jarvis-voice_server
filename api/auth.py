from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
)
from config import logger, TOKEN
from api import validate
from functions import profile as func
import json, core
from docs import schems as sh
from functions import mail


@docs(
    tags=["Profile"],
    summary="Получение профиля игрока",
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
    tags=["Auth"],
    summary="Регистрация пользователя",
    description="Регистрация нового пользователя с указанием класса и контактов",
    responses={
        201: {"description": "Регистрация успешно выполнена", "schema": sh.TokenResponseSchema},
        400: {"description": "Отсутствует один из параметров или ограничения параметра не выполнены", "schema": sh.Error400Schema},
        409: {"description": "Логин или почта заняты", "schema": sh.AlreadyBeenTaken},
        422: {"description": "Переданный email не соответствует стандартам электронной почты"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@request_schema(sh.UserRegisterSchema)
@validate.validate(validate.Register)
async def register(request: web.Request, parsed : validate.Register) -> web.Response:
    try:
        email = parsed.email
        login = parsed.login
        password = parsed.password
        
        code = await func.register_user(email, password, login)
        if not isinstance(code, str):
            return code
        await mail.send_email_register(email, code)
        return web.json_response({"token": code}, status=201)
    except Exception as e:
        logger.error("register error: ", e)
        return web.Response(status=500, text=str(e))

    
@docs(
    tags=["Auth"],
    summary="Авторизация пользователя",
    description="Получение токена авторизации",
    responses={
        200: {"description": "Авторизация успешно выполнена", "schema": sh.TokenResponseSchema},
        400: {"description": "Отсутствует один из параметров или ограничения параметра не выполнены", "schema": sh.Error400Schema},
        401: {"description": "Логин или почта не зарегистрированы"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@request_schema(sh.UserAuthSchema)
@validate.validate(validate.Auth)
async def auth(request: web.Request, parsed : validate.Auth) -> web.Response:
    try:
        identifier = parsed.identifier
        password = parsed.password
        
        code = await func.auth(identifier, password)
        return code
    except Exception as e:
        logger.error("auth error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Auth"],
    summary="Проверка активности токена",
    description="Проверка актитвен ли токен авторизации",
    responses={
        200: {"description": "Токен активный"},
        400: {"description": "Отсутствует один из параметров или ограничения параметра не выполнены", "schema": sh.Error400Schema},
        401: {"description": "Токен неактивный"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@validate.validate(validate.CheckToken)
async def check_token(request: web.Request, parsed : validate.CheckToken) -> web.Response:
    try:
        user_id = await core.check_authorization(request)
        if not isinstance(user_id, int):
            return user_id
        web.Response(status=200)
    except Exception as e:
        logger.error("auth error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Auth"],
    summary="Отправка запроса на изменение пароля",
    description="Отправка запроса на изменение пароля.",
    responses={
        204: {"description": "Запрос на изменение пароля отправлен успешно"},
        400: {"description": "Код авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        422: {"description": "Почта и телеграм аккаунт не привязаны к пользователю"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@request_schema(sh.ForgotPasswordSchema)
@validate.validate(validate.Forgot_password)
async def forgot_password(request: web.Request, parsed: validate.Forgot_password) -> web.Response:
    try:
        res = await func.forgot_password(parsed.identifier, parsed.new_password)
        return res
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))
    
@docs(
    tags=["Auth"],
    summary="Подтверждение изменения пароля",
    description="Подтверждение изменения пароля (Фонтенд не использует метод, пользователь обращается напрямую по ссылке из письма или телеграма).",
    responses={
        204: {"description": "Пароль успешно изменён"},
        400: {"description": "Код авторизации не передан", "schema": sh.Error400Schema},
        401: {"description": "Авторизация не выполнена"},
        500: {"description": "Server-side error (Ошибка на стороне сервера)"}
    }
)
@request_schema(sh.ForgotPasswordConfirmSchema)
@validate.validate(validate.Forgot_password_confirm)
async def forgot_password_confirm(request: web.Request, parsed: validate.Forgot_password_confirm) -> web.Response:
    try:
        res = await func.forgot_password_confirm(parsed.confirm)
        return res
    except Exception as e:
        logger.error("profile error: ", e)
        return web.Response(status=500, text=str(e))