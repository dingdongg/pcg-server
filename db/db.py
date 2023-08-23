import asyncio
import asyncpg
from asyncpg import Record
import json

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

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS DungeonMaps (
            id serial PRIMARY KEY,
            data jsonb NOT NULL,
            createdAt timestamptz NOT NULL
        )
        """
    )

    map1 = [
        [0, 0, 1],
        [1, 0, 1],
        [0, 0, 0],
    ]

    map_val = json.dumps(map1)
    stmt = "INSERT INTO DungeonMaps (data, createdAt) VALUES ($1, NOW())"

    await conn.execute(stmt, map_val)

    vals = await conn.fetch("SELECT * FROM DungeonMaps")
    return vals

    # rows = (("bruh", 12), ("weiojfwei", 312313), ("aaaaaa", 1111))
    # stmt = "INSERT INTO Tests (col1, col2) VALUES ($1, $2);"
    # await conn.executemany(stmt, rows)
    
    # values2 = await conn.fetch("SELECT * From Tests")

    # for v in values2:
    #     print(v["col1"], v["col2"], v["id"])

    # return values2

asyncio.run(run())