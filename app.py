from contextlib import asynccontextmanager

from litestar import Litestar, get, post, put
from litestar.exceptions import NotFoundException, ClientException
from litestar.datastructures import State
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.static_files.config import StaticFilesConfig

from typing import Any

from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

TodoType = dict[str, Any]
TodoCollectionType = list[TodoType]

class Base(DeclarativeBase):
    ...

class TodoItem(Base):
    __tablename__ = "TodoItems"

    title: Mapped[str] = mapped_column(primary_key=True)
    done: Mapped[bool]

@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    engine = getattr(app.state, "engine", None)
    if engine is None:
        engine = create_async_engine("postgresql+asyncpg://postgres:pokemon123@localhost:5432/postgres")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        app.state.engine = engine
    
    try: yield
    finally: await engine.dispose()

# a "session" (sync or async) represents one logical database transaction.
# they are not thread-safe so one instance should only be used within one DB operation
sessionmaker = async_sessionmaker(expire_on_commit=False)

def serialize_todos(todo: TodoItem) -> TodoType:
    return {
        "title": todo.title,
        "done": todo.done,
    }

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
async def get_list(state: State, done: bool | None = None) -> TodoCollectionType:
    async with sessionmaker(bind=state.engine) as session:
        return [serialize_todos(todo) for todo in await get_todo_list(done, session)]
    
@post("/")
async def add_item(data: TodoType, state: State) -> TodoType:
    new_todo = TodoItem(title=data["title"], done=data["done"])
    async with sessionmaker(bind=state.engine) as session:
        try:
            async with session.begin(): session.add(new_todo)
        except IntegrityError as e:
            raise ClientException(
                status_code=HTTP_409_CONFLICT,
                detail=f"TODO {new_todo.title} already exists",
            ) from e
        
    return serialize_todos(new_todo)

@put("/{item_title:str}")
async def update_item(item_title: str, data: TodoType, state: State) -> TodoType:
    async with sessionmaker(bind=state.engine) as session, session.begin():
        todo_item = await get_todo_by_title(item_title, session)
        todo_item.title = data["title"]
        todo_item.done = data["done"]
    
    return serialize_todos(todo_item)

route_handlers = [get_list, add_item, update_item]
static_files_config = [StaticFilesConfig(directories=["assets"], path="/favicon.ico")]

app = Litestar(route_handlers, lifespan=[ db_connection ], static_files_config=static_files_config)
