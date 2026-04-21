from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/dictionary", tags=["Metadata"])


class DictionaryEntry(BaseModel):
    name: str
    description: str
    context: str


DICTIONARY_DATA = [
    # Materials
    {"name": "composition_long_form", "description": "Full chemical formula",
     "context": "Primary identifier (e.g., Cs0.17FA0.83PbI3)"},
    {"name": "composition_inorganic", "description": "Inorganic flag",
     "context": "True for purely inorganic perovskites"},
    {"name": "band_gap", "description": "Optical band gap (eV)", "context": "Determines absorption range"},
    {"name": "tolerance_factor", "description": "Goldschmidt Factor",
     "context": "Predicts structural stability (Target: 0.8-1.0)"},
    {"name": "octahedral_factor", "description": "Octahedral Factor", "context": "Stability of BX6 octahedra"},
    {"name": "r_a / r_b / r_c", "description": "Ionic radii (Å)",
     "context": "Effective size of ions at each lattice site"},
    {"name": "is_2d", "description": "Dimensionality flag", "context": "0 = 3D, 1 = 2D (Radicati's rule)"},
    {"name": "space_group", "description": "Crystal symmetry", "context": "e.g., Cubic (Pm3m), Tetragonal (I4/mcm)"},

    # Devices
    {"name": "cell_architecture", "description": "Stacking order", "context": "nip (Regular) or pin (Inverted)"},
    {"name": "etl_stack_sequence", "description": "Electron Transport Layer",
     "context": "Extracts electrons (e.g., SnO2, TiO2)"},
    {"name": "htl_stack_sequence", "description": "Hole Transport Layer",
     "context": "Extracts holes (e.g., Spiro-MeOTAD, PTAA)"},
    {"name": "jv_default_pce", "description": "Initial Efficiency (%)",
     "context": "Power Conversion Efficiency at t=0"},
    {"name": "stability_ts80m", "description": "Standardized T80 (ML)",
     "context": "Primary target for stability prediction"},
    {"name": "acc_temp / humidity", "description": "Stress conditions",
     "context": "Acceleration factors for aging tests"},
    {"name": "perovskite_annealing_temp", "description": "Annealing Temp (°C)",
     "context": "Processing temperature for film formation"}
]


@router.get("/", response_model=List[DictionaryEntry])
async def get_dictionary():
    return DICTIONARY_DATA
