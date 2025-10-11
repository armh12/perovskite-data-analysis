from typing import List
from pydantic import BaseModel
from perovskite_prediction_api.entities.dictioanary import Element, SpaceGroup


class ElementFraction(BaseModel):
    name: Element
    frequence: float


class PerovskiteComposition(BaseModel):
    A_site: List[ElementFraction]
    B_site: List[ElementFraction]
    C_site: List[ElementFraction]


class IonicRadii(BaseModel):
    r_A: float
    r_B: float
    r_C: float


class BandGapPredictionRequest(BaseModel):
    inorganic_composition: bool
    perovskite_composition: PerovskiteComposition
    ionic_raddi: IonicRadii
    octahedral_factor: float
    tolerance_factor: float
    space_group: SpaceGroup
