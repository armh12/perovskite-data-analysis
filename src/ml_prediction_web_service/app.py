import anyio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from contextlib import asynccontextmanager

from .api.prediction_router import router as predictions_router
from .api.data_router import router as data_router
from .api.discovery_router import router as discovery_router
from .api.dictionary_router import router as dictionary_router
from .api.analysis_router import router as analysis_router
from .database import engine, Base
from . import models  # This import is crucial to register the models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Creating database tables...")
    await anyio.to_thread.run_sync(Base.metadata.create_all, engine)
    
    print("Database tables created.")
    yield
    # On shutdown
    print("Application shutdown.")

app = FastAPI(
    title="Perovskite ML Intelligence API",
    lifespan=lifespan
)

BASE_DIR = Path(__file__).resolve().parent

static_dir_path = BASE_DIR / "api" / "static"
app.mount("/static", StaticFiles(directory=static_dir_path), name="static")

templates_path = BASE_DIR / "api" / "templates"
templates = Jinja2Templates(directory=templates_path)

app.include_router(predictions_router)
app.include_router(data_router)
app.include_router(discovery_router)
app.include_router(dictionary_router)
app.include_router(analysis_router)

@app.get("/", include_in_schema=False)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
