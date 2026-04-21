import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Tuple

import joblib
from catboost import CatBoostRegressor

from ml_prediction_web_service.entities.model_dictionary import SavedModelName


class ModelRepository(ABC):
    def __init__(self):
        self._cache = {}

    @staticmethod
    def _load_model(path: str | Path) -> Any:
        return joblib.load(path)

    def _get_cached_model(self, name: SavedModelName, loader_func: Any) -> Any:
        if name not in self._cache:
            try:
                self._cache[name] = loader_func()
            except Exception as e:
                print(f"Error loading model {name}: {e}")
                return None
        return self._cache[name]

    @abstractmethod
    def get_band_gap_cat_model(self):
        pass

    @abstractmethod
    def get_band_gap_cat_quantile_models(self) -> Tuple[Any, Any]:
        pass

    @abstractmethod
    def get_pce_t80_cat_model(self):
        pass

    @abstractmethod
    def get_pce_t80_cat_quantile_models(self) -> Tuple[Any, Any]:
        pass

    @abstractmethod
    def get_initial_pce_cat_model(self):
        pass

    @abstractmethod
    def get_initial_pce_cat_quantile_models(self) -> Tuple[Any, Any]:
        pass

    @abstractmethod
    def get_ts80m_cat_model(self):
        pass

    @abstractmethod
    def get_ts80m_cat_quantile_models(self) -> Tuple[Any, Any]:
        pass

    # Legacy support
    @abstractmethod
    def get_band_gap_xgb_model(self):
        pass

    @abstractmethod
    def get_band_gap_quantile_models(self):
        pass

    @abstractmethod
    def get_pce_t80_xgb_model(self):
        pass

    @abstractmethod
    def get_pce_t80_quantile_models(self):
        pass

    @abstractmethod
    def get_jv_pce_model(self):
        pass


class LocalModelRepository(ModelRepository):
    def __init__(self, models_path: str):
        super().__init__()
        self._models_path = Path(models_path)

    def get_band_gap_cat_model(self) -> CatBoostRegressor:
        return self._get_cached_model(SavedModelName.BAND_GAP_CAT,
                                      lambda: self._load_model(self._models_path / SavedModelName.BAND_GAP_CAT.value))

    def get_band_gap_cat_quantile_models(self) -> Tuple[CatBoostRegressor, CatBoostRegressor]:
        return (
            self._get_cached_model(SavedModelName.BAND_GAP_CAT_LOW,
                                   lambda: self._load_model(self._models_path / SavedModelName.BAND_GAP_CAT_LOW.value)),
            self._get_cached_model(SavedModelName.BAND_GAP_CAT_HIGH,
                                   lambda: self._load_model(self._models_path / SavedModelName.BAND_GAP_CAT_HIGH.value))
        )

    def get_pce_t80_cat_model(self) -> CatBoostRegressor:
        return self._get_cached_model(SavedModelName.PCE_T80_CAT,
                                      lambda: self._load_model(self._models_path / SavedModelName.PCE_T80_CAT.value))

    def get_pce_t80_cat_quantile_models(self) -> Tuple[CatBoostRegressor, CatBoostRegressor]:
        return (
            self._get_cached_model(SavedModelName.PCE_T80_CAT_LOW,
                                   lambda: self._load_model(self._models_path / SavedModelName.PCE_T80_CAT_LOW.value)),
            self._get_cached_model(SavedModelName.PCE_T80_CAT_HIGH,
                                   lambda: self._load_model(self._models_path / SavedModelName.PCE_T80_CAT_HIGH.value))
        )

    def get_initial_pce_cat_model(self) -> CatBoostRegressor:
        return self._get_cached_model(SavedModelName.INITIAL_PCE_CAT, lambda: self._load_model(
            self._models_path / SavedModelName.INITIAL_PCE_CAT.value))

    def get_initial_pce_cat_quantile_models(self) -> Tuple[CatBoostRegressor, CatBoostRegressor]:
        return (
            self._get_cached_model(SavedModelName.INITIAL_PCE_CAT_LOW, lambda: self._load_model(
                self._models_path / SavedModelName.INITIAL_PCE_CAT_LOW.value)),
            self._get_cached_model(SavedModelName.INITIAL_PCE_CAT_HIGH, lambda: self._load_model(
                self._models_path / SavedModelName.INITIAL_PCE_CAT_HIGH.value))
        )

    def get_ts80m_cat_model(self) -> CatBoostRegressor:
        return self._get_cached_model(SavedModelName.TS80M_CAT,
                                      lambda: self._load_model(self._models_path / SavedModelName.TS80M_CAT.value))

    def get_ts80m_cat_quantile_models(self) -> Tuple[CatBoostRegressor, CatBoostRegressor]:
        return (
            self._get_cached_model(SavedModelName.TS80M_CAT_LOW,
                                   lambda: self._load_model(self._models_path / SavedModelName.TS80M_CAT_LOW.value)),
            self._get_cached_model(SavedModelName.TS80M_CAT_HIGH,
                                   lambda: self._load_model(self._models_path / SavedModelName.TS80M_CAT_HIGH.value))
        )

    def get_band_gap_xgb_model(self) -> CatBoostRegressor:
        return self._get_cached_model(SavedModelName.BAND_GAP_XGB,
                                      lambda: self._load_model(self._models_path / SavedModelName.BAND_GAP_XGB.value))

    def get_band_gap_quantile_models(self) -> Tuple[CatBoostRegressor, CatBoostRegressor]:
        return (self._get_cached_model(SavedModelName.BAND_GAP_LOW,
                                       lambda: self._load_model(self._models_path / SavedModelName.BAND_GAP_LOW.value)),
                self._get_cached_model(SavedModelName.BAND_GAP_HIGH, lambda: self._load_model(
                    self._models_path / SavedModelName.BAND_GAP_HIGH.value)))

    def get_pce_t80_xgb_model(self):
        return self._get_cached_model(SavedModelName.PCE_T80_XGB,
                                      lambda: self._load_model(self._models_path / SavedModelName.PCE_T80_XGB.value))

    def get_pce_t80_quantile_models(self) -> Tuple[CatBoostRegressor, CatBoostRegressor]:
        return (self._get_cached_model(SavedModelName.PCE_T80_LOW,
                                       lambda: self._load_model(self._models_path / SavedModelName.PCE_T80_LOW.value)),
                self._get_cached_model(SavedModelName.PCE_T80_HIGH,
                                       lambda: self._load_model(self._models_path / SavedModelName.PCE_T80_HIGH.value)))

    def get_jv_pce_model(self) -> CatBoostRegressor:
        return self._get_cached_model(SavedModelName.PCE_JV_XGB,
                                      lambda: self._load_model(self._models_path / SavedModelName.PCE_JV_XGB.value))
