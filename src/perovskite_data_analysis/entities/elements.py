import enum


class Elements(enum.Enum):
    def __new__(cls, *value: tuple):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0]

    @property
    def name(self) -> str:
        """Returns the name of the element/ion (e.g., 'MA')."""
        return self.value[0]

    @property
    def ionic_radii(self) -> float:
        """Returns the ionic radius of the element/ion in Ångstroms."""
        return self.value[1]

    @property
    def electronegativity(self) -> float:
        """Returns the electronegativity of the element/ion (Pauling scale)."""
        return self.value[2]

    @property
    def charge(self) -> int:
        """Returns the charge of the element/ion."""
        return self.value[3]

    @property
    def atomic_mass(self) -> float:
        """Returns the atomic mass of the element/ion in g/mol."""
        return self.value[4]

    @property
    def hydrophobicity(self) -> bool:
        """Returns whether the element/ion is hydrophobic (True/False)."""
        return self.value[5]

    @classmethod
    def get_element_by_name(cls, name: str):
        """
        Retrieves an Elements enum member by its name (e.g., 'MA', 'Pb', 'Br').

        Args:
            name (str): The name of the element/ion to find.

        Returns:
            Elements: The matching Elements enum member.

        Raises:
            ValueError: If no element with the given name is found.
        """
        for element in cls:
            if element.name == name:
                return element
        raise ValueError(f"No element found with name '{name}'")

    # A-Site Ions
    MA = ("MA", 2.17, 2.5, 1, 32.06, False)
    FA = ("FA", 2.53, 2.5, 1, 45.06, False)
    CS = ("Cs", 1.67, 0.79, 1, 132.91, False)
    BA = ("BA", 2.72, 2.5, 1, 74.14, True)
    PEA = ("PEA", 2.79, 2.5, 1, 122.18, True)
    PA = ("PA", 2.65, 2.5, 1, 60.11, True)
    RB = ("Rb", 1.52, 0.82, 1, 85.47, False)
    GU = ("GU", 2.78, 2.5, 1, 59.07, False)
    EA = ("EA", 2.43, 2.5, 1, 46.09, False)
    TMA = ("TMA", 2.80, 2.5, 1, 74.14, True)
    IPEA = ("IPEA", 2.50, 2.5, 1, 60.11, True)
    FEA = ("FEA", 2.45, 2.5, 1, 64.08, False)
    BEA = ("BEA", 2.75, 2.5, 1, 108.15, True)
    BDA = ("BDA2", 4.50, 2.5, 2, 90.17, True)
    HEA = ("HEA", 2.47, 2.5, 1, 62.09, False)
    GA = ("GA", 2.40, 2.5, 1, 76.08, False)
    NA = ("NA", 1.02, 0.93, 1, 22.99, False)
    IA = ("IA", 0.80, 1.78, 1, 114.82, False)
    CH3S = ("CH3S", 1.80, 2.58, 1, 47.10, False)
    TFEA = ("TFEA", 2.48, 2.5, 1, 100.06, False)
    NH4 = ("NH4", 1.46, 3.04, 1, 18.04, False)
    DMA = ("DMA", 2.20, 2.5, 1, 46.09, False)
    GABR3 = ("GABr3", 2.78, 2.5, 1, 59.07, False)
    THA = ("THA", 4.50, 2.5, 1, 242.46, True)
    PDA = ("PDA2", 4.20, 2.5, 2, 76.14, True)
    EU = ("EU", 1.17, 1.20, 2, 151.96, False)
    ACTA = ("ACTA", 2.55, 2.5, 1, 59.07, False)
    CIEA = ("CIEA", 2.46, 2.5, 1, 80.53, False)
    AN = ("AN", 2.70, 2.5, 1, 94.12, True)
    TEA = ("TEA", 3.50, 2.5, 1, 130.25, True)
    GNA = ("GNA", 2.78, 2.5, 1, 59.07, False)
    PNA = ("PNA", 2.65, 2.5, 1, 60.11, True)

    # B-Site Ions
    PB = ("Pb", 1.19, 2.33, 2, 207.20, False)
    SN = ("Sn", 1.10, 1.96, 2, 118.71, False)
    PBO = ("PbO", 1.19, 2.33, 2, 207.20, False)
    BI = ("Bi", 1.03, 2.02, 3, 208.98, False)
    SB = ("Sb", 0.76, 2.05, 3, 121.76, False)
    AG = ("Ag", 1.15, 1.93, 1, 107.87, False)
    BA_B = ("Ba2", 1.35, 0.89, 2, 137.33, False)
    GE = ("Ge", 0.73, 2.01, 2, 72.64, False)
    CU = ("Cu", 0.73, 1.90, 2, 63.55, False)
    MN = ("Mn", 0.83, 1.55, 2, 54.94, False)
    LA = ("La", 1.03, 1.10, 3, 138.91, False)
    TL = ("Tl", 1.50, 2.04, 1, 204.38, False)
    ZN = ("Zn", 0.74, 1.65, 2, 65.38, False)

    # X-Site Ions
    BR = ("Br", 1.96, 2.96, -1, 79.90, False)
    CL = ("Cl", 1.81, 3.16, -1, 35.45, False)
    I = ("I", 2.20, 2.66, -1, 126.90, False)
