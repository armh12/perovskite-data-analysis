from abc import ABC, abstractmethod
from typing import List

from mp_api.client import MPRester
from mp_api.client.mprester import Session
from emmet.core.mpid import MPID
from pymatgen.analysis.wulff import WulffShape
from pymatgen.core import Structure
from pymatgen.electronic_structure.bandstructure import BandStructureSymmLine
from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.io.vasp import Chgcar


class MaterialsProjectAbstractClient(ABC):
    def __init__(self, api_key: str):
        if api_key is None or len(api_key) == 0:
            raise EnvironmentError("No API key provided for Materials Project API")
        self.api_key = api_key
        # self.api_key = os.environ.get("MP_API_KEY")
        self.session = Session()
        self.mp_rester = MPRester(api_key=self.api_key,
                                  session=self.session)
        self.mp_rester.get_wulff_shape()

    @abstractmethod
    def get_materials_ids(self, formula_pattern: str) -> List[MPID]:
        """
        Returns overall material ID-s from materials project
        """
        raise NotImplementedError()

    @abstractmethod
    def search_materials(self, materials_ids: list[str]):
        """
        Get overall data for material by ID.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_band_structure(self, material_id: str | MPID) -> BandStructureSymmLine:
        """
        Return band structure for material ID.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_entries(self, material_id: str | MPID) -> ComputedStructureEntry | List[ComputedStructureEntry]:
        """
        Get structure entry for material ID.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_charge_density(self, material_id: str | MPID) -> Chgcar:
        """
        Get charge density for material ID.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_phonon_band_structure(self, material_id: str | MPID) -> BandStructureSymmLine:
        """
        Get phonon dispersion data corresponding to a material_id.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_structure(self, material_id: str | MPID, final: bool = True) -> Structure:
        """
        Get a Structure corresponding to a material_id.
        Args:
            final – Whether to get the final structure, or the list of initial (pre-relaxation) structures. Defaults to True.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_wulff_shape(self, material_id: str | MPID) -> WulffShape:
        """
        Constructs a Wulff shape for a material.
        """
        raise NotImplementedError()


class MaterialsProjectRawClient(MaterialsProjectAbstractClient):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def get_materials_ids(self, formula_pattern: str) -> List[MPID]:
        material_ids = self.mp_rester.get_materials_ids(formula_pattern)
        return material_ids

    def get_band_structure(self, material_id: str | MPID) -> BandStructureSymmLine:
        band_structure = self.mp_rester.get_band_structure(material_id)
        return band_structure

    def get_entries(self, material_id: str | MPID) -> ComputedStructureEntry | List[ComputedStructureEntry]:
        entries = self.mp_rester.get_entries(material_id)
        return entries

    def get_charge_density(self, material_id: str | MPID) -> Chgcar:
        charge_density = self.mp_rester.get_charge_density(material_id)
        return charge_density

    def get_phonon_band_structure(self, material_id: str | MPID) -> BandStructureSymmLine:
        band_structure = self.mp_rester.get_phonon_band_structure(material_id)
        return band_structure

    def get_structure(self, material_id: str | MPID, final: bool = True) -> Structure:
        structure = self.mp_rester.get_structure(material_id, final=final)
        return structure

    def get_wulff_shape(self, material_id: str | MPID) -> WulffShape:
        wulff_shape = self.mp_rester.get_wulff_shape(material_id)
        return wulff_shape
