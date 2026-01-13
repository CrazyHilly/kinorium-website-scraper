import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routers import scrape


init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Kinorium API", lifespan=lifespan)
app.include_router(scrape.router)


@app.get("/")
async def root():
    return {"status": "ok"}
