from asyncpg import Pool, Connection, create_pool
from contextlib import asynccontextmanager
from singleton_decorator import singleton
from typing import Optional, Union


@singleton
class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[Pool] = None

    async def connect(self):
        # print("Initializing database connection pool...")
        self.pool = await create_pool(self.connection_string)
        # print("Database connection pool initialized.")

    async def close(self):
        if self.pool is not None:
            await self.pool.close()

    async def execute(self, query: str, params: list, connection: Union[Connection, None] = None):
        """
        For all execute SQL statement (INSERT/UPDATE/DELETE).
        DON'T USE IT FOR SELECT queries.
        """
        if connection is not None:
            return await connection.execute(query, *params)

        async with self.pool.acquire() as conn:
            return await conn.execute(query, *params)

    async def fetch(self, query: str, params: list, connection: Union[Connection, None] = None):
        """
        For SELECT queries. When we need to query many rows
        DON'T USE IT FOR INSERT/UPDATE/DELETE queries.
        """
        if connection is not None:
            return await connection.fetch(query, *params)
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *params)

    async def fetchrow(self, query: str, params: list, connection: Union[Connection, None] = None):
        """
        For SELECT queries. When we need to query only one row
        DON'T USE IT FOR INSERT/UPDATE/DELETE queries.
        """
        if connection is not None:
            return await connection.fetchrow(query, *params)
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *params)

    async def fetchval(self, query: str, params: list, connection: Union[Connection, None] = None):
        """
        For SELECT queries where only a single value is expected.
        """
        if connection is not None:
            return await connection.fetchval(query, *params)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *params)

    @asynccontextmanager
    async def transaction(self):
        """
        Реализует контекст-менеджер транзакции.
        Пример использования:

        async with db.transaction() as conn:
            await conn.execute('INSERT ...')
            row = await conn.fetchrow('SELECT ...')
        """
        if not self.pool:
            raise RuntimeError("Pool is not initialized. Call 'connect()' first.")

        # Берём соединение
        conn = await self.pool.acquire()
        # Создаём объект транзакции
        transaction = conn.transaction()
        await transaction.start()

        try:
            # Возвращаем conn пользователю в качестве ресурса контекста
            yield conn
        except Exception:
            # Если внутри блока транзакции произошло исключение, делаем ROLLBACK
            await transaction.rollback()
            raise
        else:
            # Если всё прошло хорошо, делаем COMMIT
            await transaction.commit()
        finally:
            # В любом случае, освобождаем соединение
            await self.pool.release(conn)
