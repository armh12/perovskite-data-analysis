import os
import tempfile
from abc import ABC, abstractmethod

from xgboost import XGBRFRegressor

from perovskite_prediction_api.entities.dictioanary import SavedModelName
from perovskite_prediction_api.common.storage import GoogleDriveStorage


class AbstractModelRepository(ABC):
    @abstractmethod
    def get_band_gap_xgb_model(self):
        pass

    def _write_to_temp_file(self, model_bytes: bytes):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as f:
            f.write(model_bytes)
            tmp_path = f.name
        return tmp_path


class GoogleModelRepository(AbstractModelRepository):
    def __init__(
            self,
            google_drive: GoogleDriveStorage
    ):
        self._drive = google_drive

    def get_band_gap_xgb_model(self) -> XGBRFRegressor:
        model_bytes = self._drive.download_file("perovskite/models/band_gap_xgboost_MA_FA_Cs_Pb_I_Br.json")
        tmp_path = self._write_to_temp_file(model_bytes)
        model = XGBRFRegressor()
        model.load_model(tmp_path)
        return model
    
    
class LocalModelRepository(AbstractModelRepository):
    def __init__(
        self, models_path: str
    ):
        self._models_path = models_path
        
    def get_band_gap_xgb_model(self):
        path_to_model = os.path.join(self._models_path, SavedModelName.BAND_GAP_XGB.value)
        with open(path_to_model, "rb") as f:
            model = XGBRFRegressor()
            model.load_model(f)
        return model