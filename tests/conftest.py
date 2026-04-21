from typing import List

import pytest

from ml_prediction_web_service.entities.dictionary import Element
from ml_prediction_web_service.entities.entities import (
    BandGapPredictionRequest,
    ElementFraction,
    PerovskiteComposition,
    PCET80PredictionRequest,
    JVDefaultPCEPredictionRequest
)

PEROVSKITE_COMPOSITIONS: List[PerovskiteComposition] = [
    PerovskiteComposition(
        A_site=[ElementFraction(name=Element.CS, frequence=0.05), ElementFraction(name=Element.FA, frequence=0.79),
                ElementFraction(name=Element.MA, frequence=0.16)],
        B_site=[ElementFraction(name=Element.PB, frequence=1.0)],
        C_site=[ElementFraction(name=Element.I, frequence=2.49), ElementFraction(name=Element.BR, frequence=0.51)]
    ),
    PerovskiteComposition(
        A_site=[ElementFraction(name=Element.MA, frequence=1.0)],
        B_site=[ElementFraction(name=Element.PB, frequence=1.0)],
        C_site=[ElementFraction(name=Element.I, frequence=3.0)]
    )
]

BAND_GAP_PREDICTION_REQUESTS: List[BandGapPredictionRequest] = [
    BandGapPredictionRequest(
        perovskite_composition=PEROVSKITE_COMPOSITIONS[0],
        inorganic_composition=False
    ),
    BandGapPredictionRequest(
        perovskite_composition=PEROVSKITE_COMPOSITIONS[1],
        inorganic_composition=False
    )
]

PCE_T80_PREDICTION_REQUESTS: List[PCET80PredictionRequest] = [
    PCET80PredictionRequest(
        perovskite_composition=PEROVSKITE_COMPOSITIONS[0],
        inorganic_composition=False,
        acc_temp=25.0,
        acc_humidity=50.0,
        band_gap=1.55,
        cell_area=0.1,
        pce_initial=20.1,
        voc_initial=1.1,
        jsc_initial=22.0,
        ff_initial=0.75,
        stability_protocol="ISOS-L-1",
        stability_light_intensity=1.0,
        perovskite_annealing_temp=100.0,
        perovskite_annealing_time=10.0,
        backcontact="Au",
        etl_stack_sequence="SnO2",
        htl_stack_sequence="Spiro-MeOTAD",
        cell_architecture="nip"
    )
]

INITIAL_PCE_PREDICTION_REQUESTS: List[JVDefaultPCEPredictionRequest] = [
    JVDefaultPCEPredictionRequest(
        perovskite_composition=PEROVSKITE_COMPOSITIONS[0],
        inorganic_composition=False,
        band_gap=1.55,
        cell_area=0.1,
        perovskite_annealing_temp=100.0,
        perovskite_annealing_time=10.0,
        backcontact="Au",
        etl_stack_sequence="SnO2",
        htl_stack_sequence="Spiro-MeOTAD",
        cell_architecture="nip"
    )
]

@pytest.fixture
def band_gap_prediction_requests() -> List[BandGapPredictionRequest]:
    return BAND_GAP_PREDICTION_REQUESTS


@pytest.fixture
def pce_t80_prediction_requests() -> List[PCET80PredictionRequest]:
    return PCE_T80_PREDICTION_REQUESTS

@pytest.fixture
def initial_pce_prediction_requests() -> List[JVDefaultPCEPredictionRequest]:
    return INITIAL_PCE_PREDICTION_REQUESTS
