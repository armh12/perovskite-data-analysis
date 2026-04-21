from fastapi import APIRouter, Depends
from typing import List, Dict
from pydantic import BaseModel
from ..components import AppComponents
from ..configuration import build_components

router = APIRouter(prefix="/analysis", tags=["Model Analysis"])


class FeatureImportanceEntry(BaseModel):
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    model_name: str
    importances: List[FeatureImportanceEntry]


@router.get("/feature_importance/{target}", response_model=FeatureImportanceResponse)
async def get_feature_importance(
        target: str,
        components: AppComponents = Depends(build_components)
):
    models_map = {
        "stability": components.model_repository.get_pce_t80_cat_model,
        "band_gap": components.model_repository.get_band_gap_cat_model,
        "ts80m": components.model_repository.get_ts80m_cat_model,
        "efficiency": components.model_repository.get_initial_pce_cat_model
    }

    if target not in models_map:
        return {"error": "Invalid target model"}

    model = models_map[target]()
    if not model:
        return {"error": "Model not loaded"}

    # Get feature importance from CatBoost
    importances = model.get_feature_importance()
    feature_names = model.feature_names_

    # Sort and take top 10
    entries = []
    for name, imp in zip(feature_names, importances):
        entries.append(FeatureImportanceEntry(feature=name, importance=imp))

    entries.sort(key=lambda x: x.importance, reverse=True)

    return FeatureImportanceResponse(
        model_name=target,
        importances=entries[:12]  # Top 12 features
    )
