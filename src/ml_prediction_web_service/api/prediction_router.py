from fastapi import APIRouter, Depends

from ml_prediction_web_service.components import AppComponents
from ml_prediction_web_service.configuration import build_components
from ml_prediction_web_service.entities.entities import (
    BandGapPredictionRequest,
    PCET80PredictionRequest,
    JVDefaultPCEPredictionRequest
)

from ml_prediction_web_service.services.prediction_service import (
    predict_band_gap_service,
    predict_pce_t80_service,
    predict_jv_pce_service, predict_ts80m_service
)

router = APIRouter(prefix="/prediction", tags=["Prediction Models"])


@router.post("/band_gap")
def predict_band_gap(
        request: BandGapPredictionRequest,
        components: AppComponents = Depends(build_components)
):
    return predict_band_gap_service(request, components)


@router.post("/stability_pce_t80")
def predict_stability_pce_t80(
        request: PCET80PredictionRequest,
        components: AppComponents = Depends(build_components)
):
    return predict_pce_t80_service(request, components)


@router.post("/stability_ts80m")
def predict_stability_ts80m(
        request: PCET80PredictionRequest,
        components: AppComponents = Depends(build_components)
):
    return predict_ts80m_service(request, components)


@router.post("/jv_default_pce")
def predict_jv_default_pce(
        request: JVDefaultPCEPredictionRequest,
        components: AppComponents = Depends(build_components)
):
    return predict_jv_pce_service(request, components)
