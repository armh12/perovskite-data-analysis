import numpy as np
import pandas as pd
import pytest

from data_handler.common.data_features import decompose_sites, split_element_names

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def test_decompose_sites(df_phases):
    df_phases = decompose_sites(df_phases)
    cols = ["A_x", "A_y", "A_z", "B_x", "B_y", "B_z", "X1_x", "X1_y", "X1_z", "X2_x", "X2_y", "X2_z",
            "X3_x", "X3_y", "X3_z"]
    assert all([col in df_phases.columns for col in cols])
    assert all([df_phases[col].dtype == np.float64 for col in cols])


def test_split_element_names(df_phases):
    df_phases = split_element_names(df_phases)
    print("DF\n", df_phases)
    obj_cols = ["A_element", "B_element", "C_element"]
    num_cols = ["A_count", "B_count", "C_count"]
    assert all([obj_cols in df_phases.columns for obj_cols in obj_cols])
    assert all([df_phases[col].dtype == np.object_ for col in obj_cols])
    assert all([num_cols in df_phases.columns for num_cols in num_cols])
    assert all([df_phases[col].dtype == np.int64 for col in num_cols])


