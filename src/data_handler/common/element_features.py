from pymatgen.core import Element, get_el_sp


def get_cation_type(a_cation: str, b_cation: str):
    element = get_el_sp(element_symbol)
    print(element)
    valencies = element.common_oxidation_states
    if not valencies:
        return None
    valency = valencies[0]

    try:
        cationic_radius_A = element.average_cationic_radius
        cationic_radius_B = element.average_cationic_radius
    except:
        return None
    if cationic_radius_A > cationic_radius_B:
        return 'A'
    else:
        return 'B'

print(get_cation_type('Cs'))  # Вывод: 'A'
print(get_cation_type('Pb'))  # Вывод: 'B'
print(get_cation_type('Sn'))  # Вывод: 'B'
print(get_cation_type('Ma'))