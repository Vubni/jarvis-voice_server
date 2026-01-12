from typing import Callable, Optional, TypeVar, Awaitable, Dict, Any
from functools import wraps
from pydantic import BaseModel, ValidationError
import json
from aiohttp import web
from pydantic import field_validator, model_validator
import core


T = TypeVar("T", bound=BaseModel)


class EmailError(Exception):
    def __init__(self, message="Ошибка проверки email", errors=None):
        self.message = message
        self.errors = errors or []  # Добавляем атрибут errors
        super().__init__(self.message)


def validate(model: type[T]) -> Callable:
    def decorator(handler: Callable[[web.Request, Any], Awaitable[web.Response]]):
        @wraps(handler)
        async def wrapper(request: web.Request) -> web.Response:
            try:
                data = await request.json()
            except json.JSONDecodeError:
                data = {}

            all_data = dict(request.query)
            all_data.update(data)

            # Список чувствительных полей, которые не должны попадать в ответы об ошибках
            SENSITIVE_FIELDS = {'password', 'token',
                                'api_key', 'secret', 'authorization'}

            try:
                parsed = model(**all_data)
            except ValidationError as e:
                # Фильтруем чувствительные данные из ответа
                safe_all_data = {k: "***REDACTED***" if k.lower() in SENSITIVE_FIELDS else v
                                 for k, v in all_data.items()}

                errors = [
                    {
                        # Проверяем, есть ли элементы в loc
                        "name": error["loc"][-1] if error["loc"] else "general",
                        "type": error["type"],
                        "message": error["msg"],
                        "value": "***REDACTED***" if (error["loc"][-1] if error["loc"] else None) and
                        str(error["loc"][-1]).lower() in SENSITIVE_FIELDS
                        else (all_data.get(error["loc"][-1] if error["loc"] else None) if error["loc"] else None),
                    }
                    for error in e.errors()
                ]
                return web.json_response({
                    "error": "Validation failed",
                    "errors": errors,
                    "received_params": safe_all_data,
                }, status=400)
            except EmailError as e:
                # Фильтруем чувствительные данные из ответа
                safe_all_data = {k: "***REDACTED***" if k.lower() in SENSITIVE_FIELDS else v
                                 for k, v in all_data.items()}

                errors = [
                    {
                        "name": "email",
                        "type": "email_validation",
                        "message": e.message,
                        "value": all_data.get("email"),
                    }
                ]
                return web.json_response({
                    "error": "Email validation failed",
                    "errors": errors,
                    "received_params": safe_all_data,
                }, status=422)

            return await handler(request, parsed)
        return wrapper
    return decorator


class Command_processing(BaseModel):
    text_ru: str
    text_en: str
    save_cache: bool


class Create_session(BaseModel):
    paths: Dict[str, str]


class Auth(BaseModel):
    identifier: str
    password: str


class CheckToken(BaseModel):
    token: str


class Register(BaseModel):
    email: str
    login: str
    password: str

    @field_validator('email')
    def check_email(cls, v):
        if len(v) > 256:
            raise ValueError('Email cannot exceed 256 characters')
        if not core.is_valid_email(v):
            raise EmailError(
                'Email does not comply with email standards or dns mail servers are not found')
        return v


class Forgot_password(BaseModel):
    identifier: str
    new_password: str


class Forgot_password_confirm(BaseModel):
    confirm: str
