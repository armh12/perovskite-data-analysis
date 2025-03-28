from tests.assertions import assert_valid_oqmd_phases, assert_valid_oqmd_phases_with_set_fields, assert_valid_oqmd_calculation,\
    assert_valid_oqmd_calculation_with_set_fields, assert_valid_oqmd_structures, assert_valid_oqmd_structures_with_set_fields

MAX_PAGES = 100


def test_request_phases(oqmd_client):
    response = oqmd_client.get_phases(max_pages=MAX_PAGES)
    assert_valid_oqmd_phases(response)


def test_request_phases_when_set_generic_param_to_perovskite(oqmd_client):
    response = oqmd_client.get_phases(
        filters={"generic": "ABC3"},
        max_pages=MAX_PAGES,
    )
    assert_valid_oqmd_phases(response)


def test_request_phases_when_set_fields(oqmd_client):
    response = oqmd_client.get_phases(
        fields=["composition", "spacegroup", "volume", "ntypes", "natoms", "unit_cell", "sites", "band_gap"],
        max_pages=MAX_PAGES,
    )
    assert_valid_oqmd_phases_with_set_fields(response)


def test_request_structures(oqmd_client):
    response = oqmd_client.get_structures(max_pages=MAX_PAGES)
    assert_valid_oqmd_structures(response)


def test_request_structures_when_set_generic_param_to_perovskite(oqmd_client):
    response = oqmd_client.get_structures(
        filters={"generic": "ABC3"},
        max_pages=MAX_PAGES
    )
    assert_valid_oqmd_structures(response)


def test_request_calculations(oqmd_client):
    response = oqmd_client.get_calculations(max_pages=MAX_PAGES)
    assert_valid_oqmd_calculation(response)


def test_request_calculations_when_set_generic_param_to_perovskite(oqmd_client):
    response = oqmd_client.get_calculations(
        filters={"generic": "ABC3"},
        max_pages=MAX_PAGES,
    )
    assert_valid_oqmd_calculation(response)


def test_request_calculations_when_set_fields(oqmd_client):
    response = oqmd_client.get_calculations(
        fields=["composition", "relaxation", "band_gap", "converged", "energy_pa"],
    )
    assert_valid_oqmd_calculation_with_set_fields(response)
