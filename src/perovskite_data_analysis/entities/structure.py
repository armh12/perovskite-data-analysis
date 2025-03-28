import enum


class SpaceGroup(str, enum.Enum):
    """
    Spacegroups of perovskite materials.
    """
    RUDDLESDEN_POPEN = "I4/mmm"
    CUBIC = "Pm3m"
    TETRAGONAL = "I4/mcm"
    ORTHOROMBIC = "Pnma"