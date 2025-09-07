import enum


class BaseStructureEntity(enum.Enum):
    @property
    def code(self):
        return self.value[1]

    @classmethod
    def get_code_by_name(cls, name):
        """
        Get the code (value[1]) by spacegroup name (value[0]).
        Raises KeyError if name not found.
        """
        for member in cls:
            if member.value[0] == name:
                return member.value[1]
        raise KeyError(f"Name '{name}' not found")


class Site(enum.Enum):
    """
    Perovskite sites
    """
    A = "A"
    B = "B"
    C = "C"


class CellArchitecture(BaseStructureEntity):
    """
    Cell architecture
    """

    NIP = "nip", 1
    PIN = "pin", 2


class BackContact(BaseStructureEntity):
    """
    Back contact stacks
    """

    Au = "Au", 1
    Ag = "Ag", 2


class SpaceGroup(BaseStructureEntity):
    """
    Spacegroups of perovskite materials.
    """

    @property
    def spacegroup(self):
        return self.value[0]

    RUDDLESDEN_POPEN = "I4/mmm", 1
    CUBIC = "Pm3m", 2
    TETRAGONAL = "I4/mcm", 3
    ORTHOROMBIC = "Pnma", 4
    HEXAGONAL = 'P6/mmc', 5


class Dimensions(BaseStructureEntity):
    """
    Dimensions of perovskite materials.
    """

    @property
    def dimension(self):
        return self.value[0]

    ZERO_DIM = "0D", 0
    TWO_DIM = "2D", 1
    THREE_DIM = "3D", 2
    TWO_THREE_DIM_MIXTURE = "2D3D_mixture", 3


class ETLStacks(BaseStructureEntity):
    """
    ETL Stacks
    """

    @property
    def stack(self):
        return self.value[0]

    TWO_TI_O2_c_mp = "TiO2-c | TiO2-mp", 1
    TI_O2_c = "TiO2-c", 2
    PCBM_60 = "PCBM-60", 3
    PCBM_60_BCP = "PCBM-60 | BCP", 4
    SN_O2_np = "SnO2-np", 5
    SN_O2_c = "SnO2-c", 6
    C60_BCP = "C60 | BCP", 7
