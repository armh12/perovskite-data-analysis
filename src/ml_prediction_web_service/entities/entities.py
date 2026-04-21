import math
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, model_validator, Field

from ml_prediction_web_service.entities.dictionary import (
    Element,
    SpaceGroup,
    BackContact,
    ETLStack,
    CellArchitecture,
    Dimension,
    StabilityProtocol,
    HTLStack
)


class ElementFraction(BaseModel):
    name: Element
    frequence: float


class PerovskiteComposition(BaseModel):
    A_site: List[ElementFraction] = Field(..., examples=[[{"name": "Cs", "frequence": 0.17}, {"name": "FA", "frequence": 0.83}]])
    B_site: List[ElementFraction] = Field(..., examples=[[{"name": "Pb", "frequence": 1.0}]])
    C_site: List[ElementFraction] = Field(..., examples=[[{"name": "I", "frequence": 3.0}]])

    def __str__(self):
        def format_site(site):
            return "".join([f"{item.name.nm}{round(item.frequence, 2) if item.frequence != 1.0 else ''}" for item in site if item.frequence > 0])
        
        return f"{format_site(self.A_site)}{format_site(self.B_site)}{format_site(self.C_site)}"

    def to_short_form(self):
        # Returns a simplified version like "CsFA Pb IBr"
        def format_site(site):
            return "".join([item.name.nm for item in site if item.frequence > 0])
        
        return f"{format_site(self.A_site)} {format_site(self.B_site)} {format_site(self.C_site)}"

    @model_validator(mode='after')
    def check_fractions(self):
        total_A = sum(item.frequence for item in self.A_site)
        if not (0.99 <= total_A <= 1.01):
            raise ValueError(f'Fractions of A site must sum to 1.0, got {total_A}')

        total_B = sum(item.frequence for item in self.B_site)
        if not (0.99 <= total_B <= 1.01):
            raise ValueError(f'Fractions of B site must sum to 1.0, got {total_B}')

        total_C = sum(item.frequence for item in self.C_site)
        if not (2.99 <= total_C <= 3.01):
            raise ValueError(f'Fractions of C site must sum to 3.0, got {total_C}')
        return self


class BandGapPredictionRequest(BaseModel):
    perovskite_composition: PerovskiteComposition
    inorganic_composition: bool = Field(False, description="Whether the perovskite is purely inorganic")

    model_config = {
        "json_schema_extra": {
            "example": {
                "perovskite_composition": {
                    "A_site": [{"name": "Cs", "frequence": 0.05}, {"name": "FA", "frequence": 0.79}, {"name": "MA", "frequence": 0.16}],
                    "B_site": [{"name": "Pb", "frequence": 1.0}],
                    "C_site": [{"name": "I", "frequence": 2.49}, {"name": "Br", "frequence": 0.51}]
                },
                "inorganic_composition": False
            }
        }
    }


class BandGapPredictionResponse(BaseModel):
    band_gap: float
    lower_bound: float
    upper_bound: float
    uncertainty_range: float
    confidence_level: float = 0.90


class PCET80PredictionRequest(BaseModel):
    perovskite_composition: PerovskiteComposition
    inorganic_composition: bool
    acc_temp: float
    acc_humidity: float
    band_gap: float
    cell_area: float
    pce_initial: float
    voc_initial: float
    jsc_initial: float
    ff_initial: float
    stability_protocol: Union[StabilityProtocol, str]
    stability_light_intensity: float
    perovskite_annealing_temp: float
    perovskite_annealing_time: float
    backcontact: Union[BackContact, str]
    etl_stack_sequence: Union[ETLStack, str]
    htl_stack_sequence: Union[HTLStack, str]
    cell_architecture: Union[CellArchitecture, str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "perovskite_composition": {
                    "A_site": [{"name": "Cs", "frequence": 0.17}, {"name": "FA", "frequence": 0.83}],
                    "B_site": [{"name": "Pb", "frequence": 1.0}],
                    "C_site": [{"name": "I", "frequence": 3.0}]
                },
                "inorganic_composition": False,
                "acc_temp": 25.0,
                "acc_humidity": 50.0,
                "band_gap": 1.55,
                "cell_area": 0.1,
                "pce_initial": 20.1,
                "voc_initial": 1.1,
                "jsc_initial": 22.0,
                "ff_initial": 0.75,
                "stability_protocol": "ISOS-L-1",
                "stability_light_intensity": 1.0,
                "perovskite_annealing_temp": 100.0,
                "perovskite_annealing_time": 10.0,
                "backcontact": "Au",
                "etl_stack_sequence": "SnO2",
                "htl_stack_sequence": "Spiro-MeOTAD",
                "cell_architecture": "nip"
            }
        }
    }


class PCET80PredictionResponse(BaseModel):
    pce_t80: float
    lower_bound: float
    upper_bound: float
    uncertainty_range: float
    confidence_level: float = 0.90


class TS80MPredictionResponse(BaseModel):
    ts80m: float
    lower_bound: float
    upper_bound: float
    uncertainty_range: float
    confidence_level: float = 0.90


class JVDefaultPCEPredictionRequest(BaseModel):
    perovskite_composition: PerovskiteComposition
    inorganic_composition: bool
    band_gap: float
    cell_area: float
    perovskite_annealing_temp: float
    perovskite_annealing_time: float
    backcontact: Union[BackContact, str]
    etl_stack_sequence: Union[ETLStack, str]
    htl_stack_sequence: Union[HTLStack, str]
    cell_architecture: Union[CellArchitecture, str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "perovskite_composition": {
                    "A_site": [{"name": "MA", "frequence": 1.0}],
                    "B_site": [{"name": "Pb", "frequence": 1.0}],
                    "C_site": [{"name": "I", "frequence": 3.0}]
                },
                "inorganic_composition": False,
                "band_gap": 1.6,
                "cell_area": 0.09,
                "perovskite_annealing_temp": 100.0,
                "perovskite_annealing_time": 10.0,
                "backcontact": "Ag",
                "etl_stack_sequence": "TiO2-c | TiO2-mp",
                "htl_stack_sequence": "Spiro-MeOTAD",
                "cell_architecture": "nip"
            }
        }
    }

class JVDefaultPCEPredictionResponse(BaseModel):
    jv_default_pce: float
    lower_bound: float
    upper_bound: float
    uncertainty_range: float
    confidence_level: float = 0.90


class BandGapDiscoveryRequest(BaseModel):
    target_band_gap: float
    is_inorganic: bool = False
    max_trials: int = 50
    a_site_cations: List[str]
    c_site_anions: List[str]


class BandGapDiscoveryResponse(BaseModel):
    composition_long_form: str
    composition_short_form: str
    predicted_band_gap: float
    tolerance_factor: float
    octahedral_factor: float
    optimization_message: Optional[str] = None


class SolarPanelDiscoveryRequest(BaseModel):
    target_pce_t80: float
    is_inorganic: bool = False
    max_trials: int = 50
    a_site_cations: List[str]
    c_site_anions: List[str]
    architectures: List[str]
    etl_stacks: List[str]
    htl_stacks: List[str]
    backcontact_stacks: List[str]
    annealing_temp: Optional[float] = None
    annealing_time: Optional[float] = None


class SolarPanelDiscoveryResponse(BaseModel):
    composition_long_form: str
    composition_short_form: str
    cell_architecture: str
    etl_stack_sequence: str
    htl_stack_sequence: str
    backcontact_stack_sequence: str
    predicted_pce_t80: float
    predicted_band_gap: float
    tolerance_factor: float
    octahedral_factor: float
    optimization_message: Optional[str] = None


class PerovskiteDetailsRequest(BaseModel):
    composition_long_form: str


class PerovskiteDetailsResponse(BaseModel):
    composition_long_form: str
    composition_short_form: str
    composition_inorganic: bool
    band_gap: Optional[float]
    r_A: Optional[float]
    en_A: Optional[float]
    mass_A: Optional[float]
    r_B: Optional[float]
    en_B: Optional[float]
    mass_B: Optional[float]
    r_C: Optional[float]
    en_C: Optional[float]
    mass_C: Optional[float]
    tolerance_factor: Optional[float]
    octahedral_factor: Optional[float]
    is_2d: Optional[int]
    dimension: Optional[str]
    space_group: Optional[str]

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    def handle_nan(self):
        # Scan all fields and convert NaN to None
        for field in self.model_fields:
            value = getattr(self, field)
            if isinstance(value, float) and math.isnan(value):
                setattr(self, field, None)
        return self


class SolarPanelResponse(BaseModel):
    id: int
    data_index: Optional[int]
    composition_long_form: str
    cell_architecture: Optional[str]
    etl_stack_sequence: Optional[str]
    htl_stack_sequence: Optional[str]
    backcontact_stack_sequence: Optional[str]
    backcontact_thickness_list: Optional[str]
    jv_default_pce: Optional[float]
    jv_default_voc: Optional[float]
    jv_default_jsc: Optional[float]
    jv_default_ff: Optional[float]
    perovskite_band_gap: Optional[float]
    stability_pce_t80: Optional[float]
    stability_protocol: Optional[str]
    cell_area_measured: Optional[float]
    substrate_stack_sequence: Optional[str]
    stability_ts80: Optional[float]

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    def handle_nan(self):
        for field in self.model_fields:
            value = getattr(self, field)
            if isinstance(value, float) and math.isnan(value):
                setattr(self, field, None)
        return self
