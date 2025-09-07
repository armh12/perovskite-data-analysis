import enum


class Layers(enum.Enum):
    """
    Layers used in perovskite solar cells.
    """

    @property
    def layer_name(self):
        return self.value[0]

    @property
    def code(self):
        return self.value[1]

    @classmethod
    def get_code_by_name(cls, name):
        for member in cls:
            if member.value[0] == name:
                return member.value[1]
        raise KeyError(f"Layer name '{name}' not found")

    SLG = "SLG", 1
    FTO = "FTO", 2
    ITO = "ITO", 3
    TIO2_C = "TiO2-c", 4
    SNO2_NP = "SnO2-np", 5
    TIO2_MP = "TiO2-mp", 6
    PEROVSKITE = "Perovskite", 7
    SPIRO_MEOTAD = "Spiro-MeOTAD", 8
    AU = "Au", 9
    AG = "Ag", 10
