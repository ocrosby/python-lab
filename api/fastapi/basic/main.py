from fastapi import FastAPI

app = FastAPI(title="Basic FastAPI Example", version="1.0.0")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
