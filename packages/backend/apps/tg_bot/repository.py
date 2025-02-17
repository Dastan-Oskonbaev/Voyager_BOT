import json
import uuid

from aiogram import types
from uuid import uuid4

from packages.backend.libs.database.db_instance import db


async def init_tg_chat(chat: types.Chat, user: types.User, chat_state: str):
    new_chat_id = str(uuid4())

    async with db.transaction() as conn:
        chat_user_id = await db.fetchval(
            """
            INSERT INTO "app"."chat_user" (
                "id", "tg_user_id", "username", "first_name", "last_name", "lang_code"
            )
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5)
            ON CONFLICT ("tg_user_id") DO UPDATE
            SET
                "username" = $2,
                "first_name" = $3,
                "last_name" = $4,
                "lang_code" = $5,
                "updated_at" = timezone('utc'::text, CURRENT_TIMESTAMP)
            RETURNING "id";
            """,
            [user.id, user.username, user.first_name, user.last_name, user.language_code],
            conn
        )

        new_chat_id = await db.fetchval(
            """
            INSERT INTO "app"."chat" ("id", "tg_chat_id", "user_id", "state")
            VALUES ($1, $2, $3, $4)
            ON CONFLICT ("user_id") DO UPDATE
            SET
                "state" = $4,
                "updated_at" = timezone('utc'::text, CURRENT_TIMESTAMP)
            RETURNING "id";
            """,
            [new_chat_id, chat.id, chat_user_id, chat_state],
            conn
        )

    return new_chat_id


async def get_chat_by_remote_id(tg_chat_id: int):
    chat = await db.fetchval(
        """
        SELECT
            json_build_object(
                'id',    "id",
                'state', "state"
            )
        FROM "app"."chat"
        WHERE "tg_chat_id" = $1
        ORDER BY "created_at" DESC LIMIT 1;
        """,
        [tg_chat_id]
    )
    return json.loads(chat) if chat else None


async def update_chat_state(chat_id: str, chat_state: str):
    await db.execute(
        """
        UPDATE "app"."chat"
        SET
            "state" = $2,
            "updated_at" = timezone('utc'::text, CURRENT_TIMESTAMP)
        WHERE "id" = $1;
        """,
        [chat_id, chat_state]
    )


async def get_all_contragents_emails():
    query = """
        SELECT email
        FROM app.customers 
        WHERE email IS NOT NULL
    """
    return await db.fetch(query, [])


async def add_contragent(name: str, email: str):
    query = """
        INSERT INTO app.customers(id, username, email)
        VALUES($1, $2, $3)
    """
    await db.execute(query, [uuid.uuid4(), name, email])


async def delete_agent_by_username(username: str):
    query = """
        DELETE FROM app.customers 
        WHERE username = $1
    """
    await db.execute(query, [username])


async def get_agent_by_username(username: str):
    query = """
        SELECT email, username
        FROM app.customers 
        WHERE username = $1
    """
    return await db.fetchrow(query, [username])


async def get_all_agents():
    query = """
        SELECT array_to_json(array(
            SELECT json_build_object(
                'username', username,
                'email',    email
            )
            FROM app.customers
        ))
    """
    result = await db.fetchval(query, [])
    return json.loads(result) if result else []