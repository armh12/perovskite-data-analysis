import re
import ast
import pandas as pd


def decompose_sites(phases_df: pd.DataFrame) -> pd.DataFrame:
    def __parse_site(site_str):
        try:
            _, coords = site_str.split('@')
            x, y, z = map(float, coords.strip().split())
            return x, y, z
        except Exception:
            return None, None, None

    def __process_sites(sites_list):
        if isinstance(sites_list, str):
            try:
                sites_list = ast.literal_eval(sites_list)
            except:
                sites_list = []

        site_dict = {}

        for idx, site in enumerate(sites_list):
            x, y, z = __parse_site(site)
            if idx == 0:
                prefix = 'A'
            elif idx == 1:
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
