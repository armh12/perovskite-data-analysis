import pandas as pd
import numpy as np
import os
import sys
import re

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from ml_prediction_web_service.entities.dictionary import Element, Dimension
from ml_prediction_web_service.services.features.calc_factors import compute_tolerance_factor, compute_octahedral_factor
from ml_prediction_web_service.services.features.structure_features import compute_dimensionality_indicator, compute_space_group

def clean_messy_value(val):
    if pd.isna(val) or str(val).lower() == 'unknown' or str(val).strip() == '':
        return np.nan
    s = str(val).replace('>>', ';')
    parts = s.split(';')
    nums = []
    for p in parts:
        p_clean = p.lower().replace('unknown', '').strip()
        found = re.findall(r"[-+]?\d*\.\d+|\d+", p_clean)
        for f in found:
            try: nums.append(float(f))
            except ValueError: continue
    return np.mean(nums) if nums else np.nan

def bin_transport_layer(val):
    if pd.isna(val) or str(val).lower() in ['none', 'unknown', '']: return 'None'
    s = str(val).lower()
    if 'sno2' in s: return 'SnO2'
    if 'tio2' in s: return 'TiO2'
    if 'pedot' in s: return 'PEDOT:PSS'
    if 'spiro' in s: return 'Spiro-MeOTAD'
    if 'ptaa' in s: return 'PTAA'
    if 'c60' in s or 'pcbm' in s: return 'Fullerene'
    if 'nio' in s: return 'NiO'
    if 'zno' in s: return 'ZnO'
    return 'Other'

def parse_site_composition(elements_str, coefs_str, site_prefix, max_elements=3):
    parsed_data = {}
    elements = [e.strip() for e in str(elements_str).split(';') if e.strip() and e.strip() != 'nan' and e.strip() != 'Unknown']
    coef_raw = str(coefs_str).split(';')
    coefs = []
    for c in coef_raw:
        c_strip = c.strip()
        if c_strip and c_strip != 'nan' and c_strip != 'Unknown':
            try: coefs.append(float(c_strip))
            except ValueError: coefs.append(0.0)
    for i in range(max_elements):
        element_col = f"{site_prefix}_{i + 1}"
        coef_col = f"{site_prefix}_{i + 1}_coef"
        if i < len(elements):
            parsed_data[element_col] = elements[i]
            parsed_data[coef_col] = coefs[i] if i < len(coefs) else 0.0
        else:
            parsed_data[element_col] = None
            parsed_data[coef_col] = 0.0
    return parsed_data

def is_valid_perovskite(row):
    a_sum = sum([row.get(f'A_{i}_coef', 0) for i in range(1, 4) if pd.notna(row.get(f'A_{i}_coef'))])
    b1_name = row.get('B_1')
    b1_coef = row.get('B_1_coef', 0) if pd.notna(row.get('B_1_coef')) else 0
    c_sum = sum([row.get(f'C_{i}_coef', 0) for i in range(1, 4) if pd.notna(row.get(f'C_{i}_coef'))])
    eps = 0.05 
    is_a_valid = abs(a_sum - 1.0) < eps
    is_b_valid = (b1_name == 'Pb') and (abs(b1_coef - 1.0) < eps)
    is_c_valid = abs(c_sum - 3.0) < eps
    return is_a_valid and is_b_valid and is_c_valid

def enrich_perovskite_data(df_perov):
    def get_weighted_props(row, site_name):
        weighted_radii, weighted_en, weighted_mass, total_coef = 0.0, 0.0, 0.0, 0.0
        prefix = f"{site_name}_"
        max_idx = 4 if site_name != 'B' else 2
        for i in range(1, max_idx):
            ion_col = f"{prefix}{i}"; coef_col = f"{prefix}{i}_coef"
            if ion_col in row and pd.notna(row[ion_col]):
                ion_name = str(row[ion_col]).strip()
                coef = float(row[coef_col]) if pd.notna(row[coef_col]) else 0.0
                try:
                    element = Element.get_element_by_name(ion_name)
                    weighted_radii += coef * element.ionic_radii
                    weighted_en += coef * element.electronegativity
                    weighted_mass += coef * element.atomic_mass
                    total_coef += coef
                except Exception: continue
        if total_coef == 0: return None, None, None
        return (weighted_radii / total_coef, weighted_en / total_coef, weighted_mass / total_coef)

    for site in ['A', 'B', 'C']:
        props = df_perov.apply(lambda r: get_weighted_props(r, site), axis=1)
        df_perov[f'r_{site}'] = props.apply(lambda x: x[0] if x else None)
        df_perov[f'en_{site}'] = props.apply(lambda x: x[1] if x else None)
        df_perov[f'mass_{site}'] = props.apply(lambda x: x[2] if x else None)

    df_perov['tolerance_factor'] = df_perov.apply(lambda r: compute_tolerance_factor(r['r_A'], r['r_B'], r['r_C']), axis=1)
    df_perov['octahedral_factor'] = df_perov.apply(lambda r: compute_octahedral_factor(r['r_B'], r['r_C']), axis=1)
    df_perov['radius_ratio_ab'] = df_perov['r_A'] / df_perov['r_B']
    df_perov['en_diff_bc'] = abs(df_perov['en_B'] - df_perov['en_C'])
    df_perov['mass_ratio_ab'] = df_perov['mass_A'] / df_perov['mass_B']
    df_perov['is_2d'] = df_perov['r_A'].apply(lambda x: compute_dimensionality_indicator(x) if pd.notna(x) else 0)
    df_perov['dimension'] = df_perov['is_2d'].apply(lambda x: Dimension.TWO_DIM.nm if x == 1 else Dimension.THREE_DIM.nm)
    df_perov['space_group'] = df_perov.apply(lambda r: compute_space_group(r['tolerance_factor'], r['dimension'], r['composition_inorganic']), axis=1)
    return df_perov

def process_single_experiment_file(raw_csv_path):
    df = pd.read_csv(raw_csv_path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    perov_cols_map = {
        'Perovskite_composition_long_form': 'composition_long_form',
        'Perovskite_composition_inorganic': 'composition_inorganic',
        'Perovskite_band_gap': 'band_gap',
        'Perovskite_composition_a_ions': 'A_raw', 'Perovskite_composition_a_ions_coefficients': 'A_coef_raw',
        'Perovskite_composition_b_ions': 'B_raw', 'Perovskite_composition_b_ions_coefficients': 'B_coef_raw',
        'Perovskite_composition_c_ions': 'C_raw', 'Perovskite_composition_c_ions_coefficients': 'C_coef_raw'
    }
    df_perov_raw = df[[c for c in perov_cols_map.keys() if c in df.columns]].copy().rename(columns=perov_cols_map)
    df_perov_raw = df_perov_raw.drop_duplicates(subset=['composition_long_form']).reset_index(drop=True)

    parsed_list = []
    for _, row in df_perov_raw.iterrows():
        entry = {'composition_long_form': row['composition_long_form'], 'composition_inorganic': row['composition_inorganic'], 'band_gap': pd.to_numeric(row.get('band_gap'), errors='coerce')}
        entry.update(parse_site_composition(row.get('A_raw'), row.get('A_coef_raw'), 'A', 3))
        entry.update(parse_site_composition(row.get('B_raw'), row.get('B_coef_raw'), 'B', 1))
        entry.update(parse_site_composition(row.get('C_raw'), row.get('C_coef_raw'), 'C', 3))
        parsed_list.append(entry)

    df_perov_structured = pd.DataFrame(parsed_list)
    df_perov_structured = df_perov_structured[df_perov_structured.apply(is_valid_perovskite, axis=1)]
    df_perov_enriched = enrich_perovskite_data(df_perov_structured)

    useful_extra_cols = {
        'Perovskite_deposition_thermal_annealing_temperature': 'perovskite_annealing_temp',
        'Perovskite_deposition_thermal_annealing_time': 'perovskite_annealing_time',
        'Stability_temperature_range': 'acc_temp', 
        'Stability_relative_humidity_average_value': 'acc_humidity',
        'TS80': 'stability_ts80', 'TS80m': 'stability_ts80m'
    }
    solar_cols = [
        'Cell_architecture', 'Perovskite_composition_long_form', 'ETL_stack_sequence', 'HTL_stack_sequence', 'Backcontact_stack_sequence',
        'JV_default_PCE', 'JV_default_Voc', 'JV_default_Jsc', 'JV_default_FF',
        'Stability_PCE_T80', 'Stability_time_total_exposure', 'Stability_protocol', 'Stability_light_intensity'
    ] + list(useful_extra_cols.keys())
    
    df_solar = df[[c for c in solar_cols if c in df.columns]].copy().rename(columns={'Perovskite_composition_long_form': 'composition_long_form'})
    df_solar = df_solar.rename(columns=useful_extra_cols)

    # Clean messy columns
    for clean_col in ['perovskite_annealing_temp', 'perovskite_annealing_time', 'etl_annealing_temp', 'htl_annealing_temp', 'acc_temp', 'acc_humidity', 'stability_ts80', 'stability_ts80m']:
        if clean_col in df_solar.columns:
            df_solar[clean_col] = df_solar[clean_col].apply(clean_messy_value)

    # Keep solar panels light: remove material site/coef columns if they exist
    # but keep the join key 'composition_long_form'
    df_solar.columns = df_solar.columns.str.lower()
    
    # Filter to only device-specific columns + target columns
    device_specific_base = [
        'cell_architecture', 'composition_long_form', 'etl_stack_sequence', 'htl_stack_sequence', 'backcontact_stack_sequence',
        'jv_default_pce', 'jv_default_voc', 'jv_default_jsc', 'jv_default_ff',
        'stability_pce_t80', 'stability_time_total_exposure', 'stability_protocol', 'stability_light_intensity',
        'perovskite_annealing_temp', 'perovskite_annealing_time', 'acc_temp', 'acc_humidity', 'stability_ts80', 'stability_ts80m'
    ]
    actual_cols = [c for c in device_specific_base if c in df_solar.columns]
    df_solar_final = df_solar[actual_cols].copy()
    
    if 'jv_default_pce' in df_solar_final.columns:
        df_solar_final = df_solar_final[(df_solar_final['jv_default_pce'] > 2.0) & (df_solar_final['jv_default_pce'] < 26.0)]

    df_solar_final['etl_stack_sequence'] = df_solar_final['etl_stack_sequence'].apply(bin_transport_layer)
    df_solar_final['htl_stack_sequence'] = df_solar_final['htl_stack_sequence'].apply(bin_transport_layer)
    df_solar_final = df_solar_final[df_solar_final['backcontact_stack_sequence'].isin(['Au', 'Ag'])]
    df_solar_final = df_solar_final.reset_index(drop=True)

    return df_solar_final, df_perov_enriched

def main():
    output_dir = "../data"
    df_new_solar, df_new_perov_enriched = process_single_experiment_file(os.path.join(output_dir, "experiment_data.csv"))
    df_new_perov_enriched.to_parquet(os.path.join(output_dir, "enriched_perovskites.parquet"), index=False)
    df_new_solar.to_parquet(os.path.join(output_dir, "enriched_solar_panels.parquet"), index=False)
    print(f"Refinement Complete! Perovskites: {len(df_new_perov_enriched)} | Solar Panels: {len(df_new_solar)}")

if __name__ == "__main__":
    main()
