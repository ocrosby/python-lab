from typing import Union

from fastapi import FastAPI

app = FastAPI(
    title="Project1",
    contact={
        "name": "Omar Crosby",
        "email": "omar.crosby@gmail.com"
    }
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/health/liveness", tags=["health"])
def liveness():
    return {"status": "alive"}


@app.get("/health/readiness", tags=["health"])
def readiness():
    return {"status": "ready"}


@app.get("/health/startup", tags=["health"])
def startup():
    return {"status": "started"}
