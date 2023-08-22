from flask import Flask
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

app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=1, 
    x_proto=1, 
    x_host=1, 
    x_prefix=1,
)