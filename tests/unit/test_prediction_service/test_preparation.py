import pandas as pd
import pytest

from ml_prediction_web_service.entities.entities import (
    BandGapPredictionRequest,
    PCET80PredictionRequest,
)
from ml_prediction_web_service.services.preparation import (
    prepare_perovskites_composition_input,
    prepare_ts80_prediction_df,
)


@pytest.mark.parametrize(
    "request_entity",
    [
        BandGapPredictionRequest(
            perovskite_composition={
                "A_site": [{"name": "MA", "frequence": 1.0}],
                "B_site": [{"name": "Pb", "frequence": 1.0}],
                "C_site": [{"name": "I", "frequence": 3.0}],
            },
            inorganic_composition=False,
        )
    ],
)
def test_prepare_perovskites_composition_input(request_entity):
    df = prepare_perovskites_composition_input(request_entity)
    assert isinstance(df, pd.DataFrame)
    assert "A_1" in df.columns
    assert "A_1_coef" in df.columns
    assert df.loc[0, "A_1"] == "MA"
    assert df.loc[0, "A_1_coef"] == 1.0


def test_prepare_ts80_prediction_df(pce_t80_prediction_requests):
    request = pce_t80_prediction_requests[0]
    df = prepare_ts80_prediction_df(request)
    assert isinstance(df, pd.DataFrame)
    
    # Check for new columns
    expected_cols = [
        "acc_temp", "acc_humidity", "stress_proxy", 
        "jv_default_pce", "jv_default_voc", "jv_default_jsc", "jv_default_ff",
        "backcontact_stack_sequence", "stability_protocol"
    ]
    for col in expected_cols:
        assert col in df.columns
        
    assert df.loc[0, "acc_temp"] == 25.0
    assert df.loc[0, "acc_humidity"] == 50.0
    assert df.loc[0, "backcontact_stack_sequence"] == "Au"
