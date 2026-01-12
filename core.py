import secrets, time
import string, asyncio
import re, threading
import dns.resolver
from aiohttp import web
from config import logger
from database import functions as func_db
from functools import wraps


async def check_authorization(request:web.Request):
    try:
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                return await func_db.check_token(parts[1])
            else:
                return web.Response(status=401, text="Invalid Authorization format")
        else:
            return web.Response(status=401, text="Authorization header missing")
    except Exception as e:
        logger.error("check_authorization error: ", e)
        return web.Response(status=500, text=str(e))
    

def generate_unique_code(length:int=32):
    """Генерация рандомного кода из символов латиницы, цифры и _

    Args:
        length (int, optional): Длина кода. Defaults to 32.

    Returns:
        str: Сгенерированный код
    """
    characters = string.ascii_letters + string.digits + '_'
    return ''.join(secrets.choice(characters) for _ in range(length))


def is_domain_valid(domain):
    """Проверяет, соответствует ли домен стандартам (RFC 1035)."""
    segments = domain.split('.')
    for segment in segments:
        if not segment:
            return False
        if segment[0] == '-' or segment[-1] == '-':
            return False
        if not re.match(r'^[a-zA-Z0-9-]+$', segment):
            return False
    return True

def is_valid_email(email:str) -> bool:
    """Проверка реальности почты"""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(regex, email):
        return False

    local_part, domain_part = email.split('@')

    if len(local_part) > 64:
        return False
    if local_part.startswith('.') or local_part.endswith('.'):
        return False
    if '..' in local_part:
        return False

    if not is_domain_valid(domain_part):
        return False
    if len(domain_part) > 255:
        return False

    try:
        dns.resolver.resolve(domain_part, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.exception.Timeout):
        try:
            dns.resolver.resolve(domain_part, 'A')
            return True
        except (dns.resolver.NoAnswer, dns.exception.Timeout):
            return False
    except:
        return False
    

def is_hashable(obj):
    """Проверяет, является ли объект хешируемым."""
    try:
        hash(obj)
        return True
    except TypeError:
        return False

def cache_with_expiration(expiration_seconds: int):
    def decorator(func):
        cache = {}
        async_lock = None  # Ленивая инициализация асинхронного лока
        sync_lock = threading.Lock()

        def get_cache_key(*args, **kwargs):
            filtered_args = [arg for arg in args if is_hashable(arg)]
            filtered_kwargs = {k: v for k, v in kwargs.items() if is_hashable(v)}
            return (tuple(filtered_args), frozenset(filtered_kwargs.items()))

        @wraps(func)
        async def async_wrapped(*args, **kwargs):
            nonlocal async_lock
            if async_lock is None:
                async_lock = asyncio.Lock()  # Создаем лок в текущем event loop
            async with async_lock:
                now = time.time()
                key = get_cache_key(*args, **kwargs)
                if key in cache:
                    result, timestamp = cache[key]
                    if now - timestamp < expiration_seconds:
                        return result
                result = await func(*args, **kwargs)
                cache[key] = (result, now)
                return result

        @wraps(func)
        def sync_wrapped(*args, **kwargs):
            with sync_lock:
                now = time.time()
                key = get_cache_key(*args, **kwargs)
                if key in cache:
                    result, timestamp = cache[key]
                    if now - timestamp < expiration_seconds:
                        return result
                result = func(*args, **kwargs)
                cache[key] = (result, now)
                return result

        return async_wrapped if asyncio.iscoroutinefunction(func) else sync_wrapped

    return decorator