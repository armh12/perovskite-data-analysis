import re
import ast
import pandas as pd
from collections import Counter


def filter_perovkiste_by_name(df: pd.DataFrame) -> pd.DataFrame:
    if "name" in df.columns:
        df = df[df["name"].str.endswith("3")]
    return df


def parse_formula(formula):
    pattern = r'([A-Z][a-z]?)(\d*)'
    matches = re.findall(pattern, formula)

    composition = {}
    for (element, count) in matches:
        if count == '':
            count = 1
        else:
            count = int(count)
        if element in composition:
            composition[element] += count
        else:
            composition[element] = count
    print(composition)
    return composition


def decompose_sites(phases_df: pd.DataFrame) -> pd.DataFrame:
    def __parse_site(site_str: str):
        try:
            element, coords = site_str.split('@')
            x, y, z = map(float, coords.strip().split())
            return element, x, y, z
        except Exception:
            return None, None, None, None

    def __get_element_count(sites_list: str) -> Counter:
        elements = [site_list.split("@")[0].strip() for site_list in sites_list]
        elements_count = Counter(elements)
        return elements_count

    def __process_sites(sites_list):
        if isinstance(sites_list, str):
            try:
                sites_list = ast.literal_eval(sites_list)
            except:
                sites_list = []

        site_dict = {}
        elements_count = __get_element_count(sites_list)

        for idx, site in enumerate(sites_list):
            element, x, y, z = __parse_site(site)
            if elements_count[element] == 1:
                prefix = 'A'
            elif elements_count[element] == 1:
                prefix = 'B'
            else:
                prefix = f'X{idx - 1}'
            site_dict[f'{prefix}_x'] = x
            site_dict[f'{prefix}_y'] = y
            site_dict[f'{prefix}_z'] = z

        return pd.Series(site_dict)

    sites_expanded = phases_df["sites"].apply(__process_sites)

    phases_df = pd.concat([phases_df, sites_expanded], axis=1)
    phases_df.drop(columns=["sites"], inplace=True)
    return phases_df


def split_element_names(phases_df: pd.DataFrame):
    def __parse_composition(comp_str):
        pattern = r'([A-Z][a-z]?)(\d+)'
        matches = re.findall(pattern, comp_str)
        elements = [match[0] for match in matches]
        counts = [int(match[1]) for match in matches]
        return elements, counts

    parsed = phases_df["composition"].apply(__parse_composition)

    phases_df['A_element'] = parsed.apply(lambda x: x[0][0] if len(x[0]) > 0 else None)
    phases_df['A_count'] = parsed.apply(lambda x: x[1][0] if len(x[1]) > 0 else None)

    phases_df['B_element'] = parsed.apply(lambda x: x[0][1] if len(x[0]) > 1 else None)
    phases_df['B_count'] = parsed.apply(lambda x: x[1][1] if len(x[1]) > 1 else None)

    phases_df['C_element'] = parsed.apply(lambda x: x[0][2] if len(x[0]) > 2 else None)
    phases_df['C_count'] = parsed.apply(lambda x: x[1][2] if len(x[1]) > 2 else None)

    return phases_df
