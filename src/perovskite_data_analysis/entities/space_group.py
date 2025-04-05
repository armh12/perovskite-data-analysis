import enum


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
