"""Application entrypoint for uvicorn."""

from .main import create_app

app = create_app()
