from fastapi import fastapi

app = FastAPI()


@app.get("/")
async def root():
    return {"hello": "world"}
