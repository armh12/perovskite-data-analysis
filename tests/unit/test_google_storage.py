import pandas as pd


def test_download_file(google_storage):
    path = "perovskite/raw/idp1.pkl"
    file = google_storage.download_file(filepath=path)
    assert isinstance(file, bytes)


def test_get_file_id_by_path(google_storage):
    path = "perovskite/raw/idp1.pkl"
    file_id = google_storage._get_file_id_by_path(path)
    assert file_id is not None

    path = 'perovskite/Dataset/Structures/om140.cif'
    file_id = google_storage._get_file_id_by_path(path)
    assert file_id is not None


def test_download_dataframe(google_storage):
    path = "perovskite/raw/idx1.xlsx"
    df = google_storage.download_dataframe(path)
    assert isinstance(df, pd.DataFrame)
    print("DF\n", df)

    path = "perovskite/raw/idc1.csv"
    df = google_storage.download_dataframe(path)
    assert isinstance(df, pd.DataFrame)
    print("DF\n", df)

    path = "perovskite/raw/idp1.pkl"
    df = google_storage.download_dataframe(path)
    assert isinstance(df, pd.DataFrame)
    print("DF\n", df)

    path = 'perovskite/prepared/oqmd/phases.parquet'
    df = google_storage.download_dataframe(path)
    assert isinstance(df, pd.DataFrame)
    print("DF\n", df)
