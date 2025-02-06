"""
Module for extracting necessary features from raw OQMD data and enriching for our needs.
"""
import os
import pandas as pd

from perovskite_data_analysis.common.data_features import parse_formula, decompose_sites, split_element_names, \
    add_tolerance_factor, classify_material, parse_lattice_vectors, add_density, get_composition_features

RAW_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))
ENRICHED_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/enrich"))


def process_enrich_phases():
    phases_path = os.path.join(RAW_PATH, "phases.parquet")
    df = pd.read_parquet(phases_path)
    df["_composition"] = df["name"].apply(parse_formula)
    df = decompose_sites(df)
    df = split_element_names(df)
    df = add_tolerance_factor(df)
    df["classification"] = df["name"].apply(classify_material)
    df.drop(columns=["_composition"], inplace=True)
    df.rename(columns={"delta_e": "e_hull", "entry_id": "id"}, inplace=True)
    df.to_parquet(os.path.join(ENRICHED_PATH, "phases.parquet"))


def process_enrich_structures():
    structures_path = os.path.join(RAW_PATH, "structures.parquet")
    df = pd.read_parquet(structures_path)
    df["_composition"] = df["chemical_formula_reduced"].apply(parse_formula)
    df = parse_lattice_vectors(df)
    df = add_density(df)
    df = get_composition_features(df)
    df.rename(columns={"_oqmd_entry_id": "id"}, inplace=True)
    df.drop(columns=["_composition", "species_at_sites"], inplace=True)
    df.to_parquet(os.path.join(ENRICHED_PATH, "structures.parquet"))
