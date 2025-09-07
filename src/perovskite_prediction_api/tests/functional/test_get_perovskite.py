import pandas as pd

MAX_PAGES = 100

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def test_get_phases_returns_valid_data(perovskite_provider):
    df = perovskite_provider.get_phases(max_pages=MAX_PAGES)
    assert df is not None
    assert not df.empty
    print("Dataframe\n", df)


def test_get_structures_returns_valid_data(perovskite_provider):
    df = perovskite_provider.get_structures(max_pages=MAX_PAGES)
    assert df is not None
    assert not df.empty
    print("Dataframe\n", df)

def test_get_calculations_returns_valid_data(perovskite_provider):
    df = perovskite_provider.get_calculations(max_pages=MAX_PAGES)
    assert df is not None
    assert not df.empty
    print("Dataframe\n", df)