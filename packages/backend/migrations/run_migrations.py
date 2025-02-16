import asyncio
import os

from asyncpg import Connection
from uuid import uuid4 as uuid

from packages.backend.libs.database.db_instance import db


migrations_directory_path = os.path.join(os.path.dirname(__file__), 'files')
files = os.listdir(migrations_directory_path)


async def main():
    await db.connect()

    try:
        # Create migrations table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS "public"."migrations" (
                "id" UUID PRIMARY KEY,
                "migration_name" VARCHAR(255),
                "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            []
        )

        # Get the list of already applied transactions
        result = await db.fetch('SELECT "migration_name" FROM "public"."migrations";', [])
        applied_migrations = [row['migration_name'] for row in result]

        async with db.transaction() as conn:
            for migration_name in sorted(files):
                if migration_name in applied_migrations:
                    continue

                file_path = os.path.join(migrations_directory_path, migration_name)

                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8') as migration_file:
                        query = migration_file.read()
                        await conn.execute(query)
                        await conn.execute(
                            """
                            INSERT INTO migrations ("id", "migration_name")
                            VALUES ($1, $2);
                            """,
                            str(uuid()), migration_name
                        )
                        print('Migration', migration_name, 'applied')

        print("Migrations applied")
    except Exception as e:
        print(f"Run migrations error: {e}")
    finally:
        await db.close()


if __name__ == '__main__':
    asyncio.run(main())
