import pytest
from unittest.mock import MagicMock
import numpy as np

from ml_prediction_web_service.services.prediction_service import (
    predict_band_gap_service,
    predict_pce_t80_service,
    predict_ts80m_service,
    predict_jv_pce_service
)
from ml_prediction_web_service.entities.entities import (
    BandGapPredictionResponse,
    PCET80PredictionResponse,
    TS80MPredictionResponse,
    JVDefaultPCEPredictionResponse
)


def test_predict_band_gap_service(band_gap_prediction_requests):
    components = MagicMock()
    model = MagicMock()
    model.predict.return_value = [1.6]
    components.model_repository.get_band_gap_cat_model.return_value = model
    
    low_m, high_m = MagicMock(), MagicMock()
    low_m.predict.return_value = [1.55]
    high_m.predict.return_value = [1.65]
    components.model_repository.get_band_gap_cat_quantile_models.return_value = (low_m, high_m)
    
    response = predict_band_gap_service(band_gap_prediction_requests[0], components)
    
    assert isinstance(response, BandGapPredictionResponse)
    assert response.band_gap == 1.6
    assert response.lower_bound == 1.55
    assert response.upper_bound == 1.65


def test_predict_pce_t80_service(pce_t80_prediction_requests):
    components = MagicMock()
    model = MagicMock()
    model.predict.return_value = [6.908755] # log(1+1000)
    components.model_repository.get_pce_t80_cat_model.return_value = model

    low_m, high_m = MagicMock(), MagicMock()
    low_m.predict.return_value = [6.216606] # log(1+500)
    high_m.predict.return_value = [7.31391] # log(1+1500)
    components.model_repository.get_pce_t80_cat_quantile_models.return_value = (low_m, high_m)
    
    response = predict_pce_t80_service(pce_t80_prediction_requests[0], components)
    
    assert isinstance(response, PCET80PredictionResponse)
    assert round(response.pce_t80) == 1000
    assert round(response.lower_bound) == 500
    assert round(response.upper_bound) == 1500


def test_predict_ts80m_service(pce_t80_prediction_requests):
    components = MagicMock()
    model = MagicMock()
    model.predict.return_value = [6.216606] # log(1+500)
    components.model_repository.get_ts80m_cat_model.return_value = model

    low_m, high_m = MagicMock(), MagicMock()
    low_m.predict.return_value = [5.70711] # log(1+300)
    high_m.predict.return_value = [6.552508] # log(1+700)
    components.model_repository.get_ts80m_cat_quantile_models.return_value = (low_m, high_m)
    
    response = predict_ts80m_service(pce_t80_prediction_requests[0], components)
    
    assert isinstance(response, TS80MPredictionResponse)
    assert round(response.ts80m) == 500
    assert round(response.lower_bound) == 300
    assert round(response.upper_bound) == 700


def test_predict_jv_pce_service(initial_pce_prediction_requests):
    components = MagicMock()
    model = MagicMock()
    model.predict.return_value = [20.5]
    components.model_repository.get_initial_pce_cat_model.return_value = model

    low_m, high_m = MagicMock(), MagicMock()
    low_m.predict.return_value = [19.0]
    high_m.predict.return_value = [22.0]
    components.model_repository.get_initial_pce_cat_quantile_models.return_value = (low_m, high_m)
    
    response = predict_jv_pce_service(initial_pce_prediction_requests[0], components)
    
    assert isinstance(response, JVDefaultPCEPredictionResponse)
    assert response.jv_default_pce == 20.5
    assert response.lower_bound == 19.0
    assert response.upper_bound == 22.0
