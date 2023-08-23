from typing import Any

from dataclasses import dataclass
from litestar import Litestar, get, post, put
from litestar.exceptions import NotFoundException

@dataclass
class TodoItem:
    title: str
    done: bool

TODO_LIST: list[TodoItem] = [
    TodoItem(title="Start writing TODO list", done=True),
    TodoItem(title="???", done=False),
    TodoItem(title="Profit", done=False),
]

@get("/")
async def get_lists(done: bool = None) -> list[TodoItem]:
    if done is None: return TODO_LIST
    return [item for item in TODO_LIST if item.done == done]

def find_item(title: str) -> TodoItem:
    for item in TODO_LIST:
        if item.title == title: return item
    raise NotFoundException(detail=f"TODO {title} not found")

@put("/{title:str}")
async def update_item(title: str, data: TodoItem) -> list[TodoItem]:
    item = find_item(title)
    item.title = data.title
    item.done = data.done
    return TODO_LIST

@post("/")
async def add_item(data: TodoItem) -> list[TodoItem]:
    TODO_LIST.append(data)
    return TODO_LIST

app = Litestar([ get_lists, add_item, update_item ])