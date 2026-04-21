import numpy as np
import pandas as pd

from ml_prediction_web_service.components import AppComponents
from ml_prediction_web_service.entities.entities import (
    BandGapPredictionRequest,
    BandGapPredictionResponse,
    PCET80PredictionRequest,
    PCET80PredictionResponse,
    TS80MPredictionResponse,
    JVDefaultPCEPredictionResponse,
    JVDefaultPCEPredictionRequest
)
from ml_prediction_web_service.services.preparation import (
    prepare_perovskites_composition_input,
    prepare_ts80_prediction_df,
    prepare_jv_pce_prediction_df
)


def predict_band_gap_service(
        request: BandGapPredictionRequest,
        components: AppComponents
) -> BandGapPredictionResponse:
    df = prepare_perovskites_composition_input(request)
    model = components.model_repository.get_band_gap_cat_model()
    low_m, high_m = components.model_repository.get_band_gap_cat_quantile_models()
    
    prediction = float(model.predict(df)[0])
    low = float(low_m.predict(df)[0]) if low_m else prediction * 0.95
    high = float(high_m.predict(df)[0]) if high_m else prediction * 1.05
    
    return BandGapPredictionResponse(
        band_gap=prediction,
        lower_bound=low,
        upper_bound=high,
        uncertainty_range=high - low
    )


def predict_pce_t80_service(
        request: PCET80PredictionRequest,
        components: AppComponents
) -> PCET80PredictionResponse:
    df = prepare_ts80_prediction_df(request)
    
    model = components.model_repository.get_pce_t80_cat_model()
    low_m, high_m = components.model_repository.get_pce_t80_cat_quantile_models()
    
    prediction_log = model.predict(df)[0]
    prediction = float(np.expm1(prediction_log))
    
    low = float(np.expm1(low_m.predict(df)[0])) if low_m else prediction * 0.7
    high = float(np.expm1(high_m.predict(df)[0])) if high_m else prediction * 1.3

    return PCET80PredictionResponse(
        pce_t80=prediction,
        lower_bound=low,
        upper_bound=high,
        uncertainty_range=high - low
    )


def predict_ts80m_service(
        request: PCET80PredictionRequest,
        components: AppComponents
) -> TS80MPredictionResponse:
    df = prepare_ts80_prediction_df(request)
    
    model = components.model_repository.get_ts80m_cat_model()
    low_m, high_m = components.model_repository.get_ts80m_cat_quantile_models()
    
    prediction_log = model.predict(df)[0]
    prediction = float(np.expm1(prediction_log))

    low = float(np.expm1(low_m.predict(df)[0])) if low_m else prediction * 0.7
    high = float(np.expm1(high_m.predict(df)[0])) if high_m else prediction * 1.3

    return TS80MPredictionResponse(
        ts80m=prediction,
        lower_bound=low,
        upper_bound=high,
        uncertainty_range=high - low
    )


def predict_jv_pce_service(
        request: JVDefaultPCEPredictionRequest,
        components: AppComponents
) -> JVDefaultPCEPredictionResponse:
    df = prepare_jv_pce_prediction_df(request)
    
    model = components.model_repository.get_initial_pce_cat_model()
    low_m, high_m = components.model_repository.get_initial_pce_cat_quantile_models()
    
    prediction = float(model.predict(df)[0])
    low = float(low_m.predict(df)[0]) if low_m else prediction * 0.85
    high = float(high_m.predict(df)[0]) if high_m else prediction * 1.15

    return JVDefaultPCEPredictionResponse(
        jv_default_pce=prediction,
        lower_bound=low,
        upper_bound=high,
        uncertainty_range=high - low
    )
