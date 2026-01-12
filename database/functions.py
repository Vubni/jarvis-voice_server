from database.database import Database
from aiohttp import web

async def check_token(token):
    async with Database() as db:
        await db.execute("DELETE FROM tokens WHERE date < CURRENT_DATE - INTERVAL '1 month'")
        res = await db.execute("SELECT user_id FROM tokens WHERE token=$1", (token,))
        if not res:
            return web.Response(status=401, text="Invalid token")
    return res["user_id"]

async def init_db():
    async with Database() as db:
        try:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.users
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    email character varying(256) COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    login character varying(20) COLLATE pg_catalog."default" NOT NULL,
    register date DEFAULT CURRENT_DATE,
    verified boolean DEFAULT false,
    CONSTRAINT users_pkey PRIMARY KEY (id)
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.tokens
(
    token character varying(32) COLLATE pg_catalog."default" NOT NULL,
    user_id bigint NOT NULL,
    date date NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT tokens_pkey PRIMARY KEY (token),
    CONSTRAINT tokens_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.subscription
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9999999999999999 CACHE 1 ),
    type integer NOT NULL,
    price integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    user_id bigint NOT NULL,
    CONSTRAINT subscription_pkey PRIMARY KEY (id),
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)""")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS public.commands
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 999999999999999999 CACHE 1 ),
    user_id bigint NOT NULL,
    phrase character varying(256) COLLATE pg_catalog."default" NOT NULL,
    command character varying(512) COLLATE pg_catalog."default" NOT NULL,
    answer character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT commands_pkey PRIMARY KEY (id),
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)""")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")