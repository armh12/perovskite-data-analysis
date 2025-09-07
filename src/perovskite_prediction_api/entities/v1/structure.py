import enum


class Sites(enum.Enum):
    """
    Perovskite sites
    """
    A = "A"
    B = "B"
    C = "C"

class SpaceGroup(enum.Enum):
    """
    Spacegroups of perovskite materials.
    """

    @property
    def spacegroup(self):
        return self.value[0]

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
        raise KeyError(f"Spacegroup name '{name}' not found")

    RUDDLESDEN_POPEN = "I4/mmm", 1
    CUBIC = "Pm3m", 2
    TETRAGONAL = "I4/mcm", 3
    ORTHOROMBIC = "Pnma", 4
    HEXAGONAL = 'P6/mmc', 5


class Dimensions(enum.Enum):
    """
    Dimensions of perovskite materials.
    """

    @property
    def dimension(self):
        return self.value[0]

    @property
    def code(self):
        return self.value[1]

    @classmethod
    def get_code_by_name(cls, name):
        """
        Get the code (value[1]) by dimension name (value[0]).
        Raises KeyError if name not found.
        """
        for member in cls:
            if member.value[0] == name:
                return member.value[1]
        raise KeyError(f"Dimension name '{name}' not found")

    ZERO_DIM = ("0D", 0)
    TWO_DIM = ("2D", 1)
    THREE_DIM = ("3D", 2)
    TWO_THREE_DIM_MIXTURE = ("2D3D_mixture", 3)
