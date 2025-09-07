import numpy as np
import pandas as pd

from perovskite_prediction_api.features.complex import decompose_sites, split_element_names, \
    get_composition_features, classify_material, add_tolerance_factor, parse_formula, parse_lattice_vectors

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
    obj_cols = ["A_element", "B_element", "C_element"]
    num_cols = ["A_count", "B_count", "C_count"]
    assert all([obj_cols in df_phases.columns for obj_cols in obj_cols])
    assert all([df_phases[col].dtype == np.object_ for col in obj_cols])
    assert all([num_cols in df_phases.columns for num_cols in num_cols])
    assert all([df_phases[col].dtype == np.int64 for col in num_cols])


def test_get_composition_features(df_structures):
    df_structures = get_composition_features(df_structures)
    assert "weight" in df_structures.columns
    assert "avg_elec_negativity" in df_structures.columns
    assert df_structures["weight"].dtype == np.float64
    assert df_structures["avg_elec_negativity"].dtype == np.float64

def test_classify_material(df_structures):
    df_structures["classification"] = df_structures["chemical_formula_reduced"].apply(classify_material)
    assert "classification" in df_structures.columns
    assert df_structures["classification"].dtype == np.object_


def test_add_tolerance_factor(df_phases):
    df_phases["_composition"] = df_phases["name"].apply(parse_formula)
    df_phases = split_element_names(df_phases)
    df_phases = add_tolerance_factor(df_phases)
    assert "tolerance_factor" in df_phases.columns
    assert df_phases["tolerance_factor"].dtype == np.float64


def test_parse_lattice_vectors(df_structures):
    df_structures = parse_lattice_vectors(df_structures)
    print(df_structures)
