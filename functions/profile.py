from database.database import Database
import json, re
import core
from typing import List, Optional
from asyncpg import Record
from aiohttp import web
import config
from functions import mail


async def verify_email(user_id:int):
    async with Database() as db:
        email = (await db.execute("SELECT email FROM users WHERE id=$1", (user_id,)))["email"]
        await db.execute("UPDATE users SET verified=true WHERE email=$1", (email,))

async def register_user(email : str, password : str, login: str) -> str:
    """Регистрация нового пользователя в системе

    Args:
        login (str): _description_
        email (str): _description_
        password (str): _description_

    Returns:
        str: _description_
    """
    async with Database() as db:
        res = await db.execute("SELECT 1 FROM users WHERE email = $1", (email,))
        if res:
            return web.json_response({"name": "email", "error": "The email has already been registered"}, status=409)
        res = await db.execute("SELECT 1 FROM users WHERE login = $1", (login,))
        if res:
            return web.json_response({"name": "login", "error": "The login has already been registered"}, status=409)
        
        await db.execute(
            "INSERT INTO users (login, email, password) VALUES ($1, $2, $3)",
            (login, email, password)
        )
        user_id = (await db.execute("SELECT id FROM users WHERE login=$1", (login,)))["id"]
        await db.execute("DELETE FROM tokens WHERE date < CURRENT_DATE - INTERVAL '1 month'")
        code = core.generate_unique_code()
        await db.execute("INSERT INTO tokens (user_id, token) VALUES ($1, $2)", (user_id, code,))
        await db.execute("INSERT INTO subjects (email, subject) VALUES ($1, $2)", (email, "Русский язык",))
    return code

async def auth(identifier:str, password:str) -> str:
    async with Database() as db:
        res = await db.execute("SELECT id FROM users WHERE (email = $1 or login = $1) AND password=$2", (identifier, password))
        if not res:
            return web.Response(status=401, text="The identifier information is incorrect")
        user_id = res["id"]
        await db.execute("DELETE FROM tokens WHERE date < CURRENT_DATE - INTERVAL '1 month'")
        code = core.generate_unique_code()
        await db.execute("INSERT INTO tokens (user_id, token) VALUES ($1, $2)", (user_id, code,))
    return web.json_response({"token": code}, status=200)

async def forgot_password(identifier: str, new_password: str) -> web.Response:
    async with Database() as db:
        res = await db.execute("SELECT id, email FROM users WHERE (email = $1 or login = $1)", (identifier,))
        if not res:
            return web.Response(status=401, text="The login information is incorrect")
        if not res["email"]:
            return web.Response(status=422, text="Email and Telegram account are not linked to the user")
        result = await db.fetchval("INSERT INTO new_password_wait (user_id, new_password) VALUES ($1, $2)", (res["id"], new_password,))
        if res["email"]:
            await mail.send_password_edit(res["email"], f"https://api.vubni.com/auth/forgot_password/confirm?confirm={result}")
        return web.Response(status=204)
    
async def forgot_password_confirm(confirm: int) -> web.Response:
    async with Database() as db:
        res = await db.execute("SELECT user_id, new_password FROM new_password_wait WHERE id = $1", (confirm,))
        if not res:
            return web.Response(status=400, text="Invalid confirmation code")
        await db.execute("UPDATE users SET password=$1 WHERE id=$2", (res["new_password"], res["user_id"],))
        await db.execute("DELETE FROM new_password_wait WHERE id=$1", (confirm,))
        return web.Response(status=204)

async def subscripe(user_id:int):
    async with Database() as db:
        await db.execute("SELECT ")
        
