from fastapi import FastAPI
from app.routers import scrape

app = FastAPI(title="Kinorium API")
app.include_router(scrape.router)


@app.get("/")
async def root(): 
    return {"status": "ok"}
