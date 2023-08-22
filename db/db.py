import asyncio
import asyncpg
from asyncpg import Record

async def run() -> list[Record]:
    conn_str = "postgres://postgres:pokemon123@127.0.0.1:5432/postgres"
    conn = await asyncpg.connect(conn_str)
    values = await conn.fetch(
        "SELECT * FROM Users"
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Tests (
            id serial PRIMARY KEY,
            col1 VARCHAR(255) NOT NULL,
            col2 INT NOT NULL
        )
        """
    )

    # rows = (("bruh", 12), ("weiojfwei", 312313), ("aaaaaa", 1111))
    # stmt = "INSERT INTO Tests (col1, col2) VALUES ($1, $2);"
    # await conn.executemany(stmt, rows)
    
    values2 = await conn.fetch("SELECT * From Tests")

    # for v in values2:
    #     print(v["col1"], v["col2"], v["id"])

    return values2

asyncio.run(run())