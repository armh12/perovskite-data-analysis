import tempfile
from abc import ABC, abstractmethod

from xgboost import XGBRFRegressor

from perovskite_prediction_api.common.storage import GoogleDriveStorage


class AbstractModelRepository(ABC):
    @abstractmethod
    def get_band_gap_model_for_3d_perovskites(self):
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

    def get_band_gap_model_for_3d_perovskites(self) -> XGBRFRegressor:
        model_bytes = self._drive.download_file("perovskite/models/band_gap_xgboost_MA_FA_Cs_Pb_I_Br.json")
        tmp_path = self._write_to_temp_file(model_bytes)
        model = XGBRFRegressor()
        model.load_model(tmp_path)
        return model
