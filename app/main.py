from fastapi import FastAPI

app = FastAPI(title="Kinorium API")


@app.get("/")
async def root(): 
    return {"status": "ok"}
