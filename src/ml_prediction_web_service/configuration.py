import os
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session

from dotenv import load_dotenv

from ml_prediction_web_service.components import AppComponents
from ml_prediction_web_service.repository.model_repository import LocalModelRepository
from ml_prediction_web_service.repository.data_repository import DataRepository
from ml_prediction_web_service.database import get_db, SessionLocal

load_dotenv()

MODELS_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ml_models"))


def get_model_path() -> str:
    models_path = os.environ.get("MODELS_PATH", MODELS_BASE_PATH)
    if not os.path.isdir(models_path):
        # This is a fallback for when the env var is not set, e.g. in tests
        # In a real app, you might want to raise an error if the path is critical
        os.makedirs(models_path, exist_ok=True)
    return models_path


@lru_cache
def get_model_repository() -> LocalModelRepository:
    path = get_model_path()
    return LocalModelRepository(path)


def get_data_repository(db: Session = Depends(get_db)) -> DataRepository:
    return DataRepository(db)


def build_components(
        model_repo: LocalModelRepository = Depends(get_model_repository),
        data_repo: DataRepository = Depends(get_data_repository)
) -> AppComponents:
    return AppComponents(
        model_repository=model_repo,
        data_repository=data_repo
    )
