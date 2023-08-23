from flask import Flask, request
from db.db import run
import asyncio
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

@app.get("/")
def bruh():
    res = asyncio.run(run())
    dto = list(map(lambda r: dict(r), res))
    return dto

@app.get("/hello")
def hello():
    return "hello world"

@app.get("/map")
def get_map():
    dungeon_maps = asyncio.run(run())
    dto = list(map(lambda m: dict(m), dungeon_maps))
    return dto

app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=1, 
    x_proto=1, 
    x_host=1, 
    x_prefix=1,
)