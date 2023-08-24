from litestar import Litestar, get, post, put
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemySerializationPlugin,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)
from litestar.exceptions import NotFoundException, ClientException
from litestar.datastructures import State
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.static_files.config import StaticFilesConfig

from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    ...

class TodoItem(Base):
    __tablename__ = "TodoItems"

    title: Mapped[str] = mapped_column(primary_key=True)
    done: Mapped[bool]

async def provide_transaction(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

async def get_todo_by_title(todo_name: str, session: AsyncSession) -> TodoItem:
    query = select(TodoItem).where(TodoItem.title == todo_name)
    result = await session.execute(query)

    try: return result.scalar_one()
    except NoResultFound as e: raise NotFoundException(detail=f"TODO {todo_name} not found") from e

async def get_todo_list(done: bool | None, session: AsyncSession) -> list[TodoItem]:
    query = select(TodoItem)
    if done is not None:
        query = query.where(TodoItem.done.is_(done))

    result = await session.execute(query)
    return result.scalars().all()

@get("/")
async def get_list(transaction: AsyncSession, done: bool | None = None) -> list[TodoItem]:
    print("HASH:", transaction.__hash__())
    return await get_todo_list(done, transaction)
    
@post("/")
async def add_item(data: TodoItem, transaction: AsyncSession) -> TodoItem:
    transaction.add(data)

    return data

@put("/{item_title:str}")
async def update_item(item_title: str, data: TodoItem, transaction: AsyncSession) -> TodoItem:
    todo_item = await get_todo_by_title(item_title, transaction)
    todo_item.title = data.title
    todo_item.done = data.done
    
    return todo_item

# DB configuration
db_config = SQLAlchemyAsyncConfig(connection_string="postgresql+asyncpg://postgres:pokemon123@localhost:5432/postgres")

# Litestar app args
route_handlers = [get_list, add_item, update_item]
static_files_config = [StaticFilesConfig(directories=["assets"], path="/favicon.ico")]
plugins = [
    SQLAlchemySerializationPlugin(), # de/serialize out/ingoing payloads
    SQLAlchemyInitPlugin(db_config), # configures and manages the DB engine and request-level sessions
]

app = Litestar(
    route_handlers, 
    static_files_config=static_files_config,
    dependencies={ "transaction": provide_transaction }, # use dependency injection to create transactions beforehand
    plugins=plugins,
)
