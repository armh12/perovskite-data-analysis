OQMD_PHASES_COLUMNS = ["name", "composition", "composition_generic", "prototype", "spacegroup", "fit", "unit_cell",
                       "ntypes", "natoms", "band_gap", "delta_e", "stability"]


def assert_valid_oqmd_phases(phases_response):
    assert isinstance(phases_response, list)
    single_data = phases_response[0]
    assert isinstance(single_data, dict)
    assert "name" in single_data
    assert "composition" in single_data
    assert "composition_generic" in single_data
    assert "prototype" in single_data
    assert "spacegroup" in single_data
    assert "fit" in single_data

    assert isinstance(single_data["unit_cell"], list)
    assert isinstance(single_data["ntypes"], int)
    assert isinstance(single_data["natoms"], int)
    assert isinstance(single_data["band_gap"], float)
    assert isinstance(single_data["delta_e"], float)
    assert isinstance(single_data["stability"], float)


def assert_valid_oqmd_phases_with_set_fields(phases_response: list):
    single_data = phases_response[0]
    fields = list(single_data.keys())
    assert len(fields) != len(OQMD_PHASES_COLUMNS)
    assert sorted(fields) != sorted(OQMD_PHASES_COLUMNS)


def assert_valid_oqmd_structures(structures_response):
    assert isinstance(structures_response, list)
    single_data = structures_response[0]
    assert isinstance(single_data, dict)
    assert isinstance(single_data["id"], int)
    assert "type" in single_data and single_data["type"] == 'structures'
    attrs = single_data["attributes"]
    assert isinstance(attrs, dict)
    assert "chemical_formula_reduced" in attrs
    assert "chemical_formula_anonymous" in attrs
    assert "chemical_formula_descriptive" in attrs
    assert "_oqmd_prototype" in attrs
    assert "_oqmd_spacegroup" in attrs
    assert isinstance(attrs["nelements"], int)
    assert isinstance(attrs["elements"], list)
    assert isinstance(attrs["nsites"], int)
    assert isinstance(attrs["lattice_vectors"], list)
    assert isinstance(attrs["species_at_sites"], list)
    assert isinstance(attrs["nperiodic_dimensions"], int)
    assert isinstance(attrs["structure_features"], list)
    assert isinstance(attrs["cartesian_site_positions"], list)
    assert isinstance(attrs["_oqmd_band_gap"], float)
    assert isinstance(attrs["_oqmd_delta_e"], float)
    assert isinstance(attrs["_oqmd_volume"], float)
    assert isinstance(attrs["_oqmd_stability"], float)


def assert_valid_oqmd_structures_with_set_fields(structures_response: list):
    single_data = structures_response[0]
    print(single_data)



