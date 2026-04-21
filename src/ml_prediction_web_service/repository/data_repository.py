from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from typing import List, Optional, Dict, Any
from .. import models


class DataRepository:
    def __init__(self, db: Session):
        self.db = db

    def ingest_from_parquet(self, perovskites_path: str, solar_panels_path: str):
        from ..entities.entities import PerovskiteComposition, ElementFraction
        from ..entities.dictionary import Element

        df_p = pd.read_parquet(perovskites_path)
        df_p = df_p.where(pd.notnull(df_p), None)
        
        # We need to populate composition_short_form
        def get_short_form(row):
            try:
                a_site = []
                for i in range(1, 4):
                    if row[f'A_{i}']:
                        a_site.append(ElementFraction(name=Element(row[f'A_{i}']), frequence=row[f'A_{i}_coef'] or 0.0))
                b_site = [ElementFraction(name=Element(row['B_1']), frequence=row['B_1_coef'] or 0.0)]
                c_site = []
                for i in range(1, 4):
                    if row[f'C_{i}']:
                        c_site.append(ElementFraction(name=Element(row[f'C_{i}']), frequence=row[f'C_{i}_coef'] or 0.0))
                
                comp = PerovskiteComposition(A_site=a_site, B_site=b_site, C_site=c_site)
                return comp.to_short_form()
            except Exception:
                return "Unknown"

        df_p['composition_short_form'] = df_p.apply(get_short_form, axis=1)
        p_data = df_p.to_dict(orient='records')

        existing_p = {item[0] for item in self.db.query(models.Perovskite.composition_long_form).all()}
        new_perovskites = [models.Perovskite(**row) for row in p_data if row['composition_long_form'] not in existing_p]

        if new_perovskites:
            self.db.bulk_save_objects(new_perovskites)
            self.db.commit()

        # Re-fetch all valid perovskites to ensure solar panels match
        valid_compositions = {item[0] for item in self.db.query(models.Perovskite.composition_long_form).all()}

        df_s = pd.read_parquet(solar_panels_path)
        df_s = df_s.where(pd.notnull(df_s), None)
        if 'index' in df_s.columns:
            df_s.rename(columns={'index': 'data_index'}, inplace=True)
            
        # Filter df_s to only those in valid_compositions
        df_s = df_s[df_s['composition_long_form'].isin(valid_compositions)]
        
        s_data = df_s.to_dict(orient='records')

        new_panels = [models.SolarPanel(**row) for row in s_data]
        if new_panels:
            self.db.bulk_save_objects(new_panels)
            self.db.commit()

        return len(new_perovskites), len(new_panels)

    def get_perovskites(self, offset: int = 0, limit: int = 100) -> List[models.Perovskite]:
        return self.db.query(models.Perovskite).offset(offset).limit(limit).all()

    def get_perovskite_by_composition(self, composition_long_form: str) -> Optional[models.Perovskite]:
        return self.db.query(models.Perovskite).filter(
            models.Perovskite.composition_long_form == composition_long_form).first()

    def add_perovskite(self, perovskite_data: Dict[str, Any]) -> models.Perovskite:
        db_p = models.Perovskite(**perovskite_data)
        self.db.add(db_p)
        self.db.commit()
        self.db.refresh(db_p)
        return db_p

    def get_solar_panels(self, offset: int = 0, limit: int = 100) -> List[models.SolarPanel]:
        return self.db.query(models.SolarPanel).offset(offset).limit(limit).all()

    def add_solar_panel(self, panel_data: Dict[str, Any]) -> models.SolarPanel:
        db_s = models.SolarPanel(**panel_data)
        self.db.add(db_s)
        self.db.commit()
        self.db.refresh(db_s)
        return db_s

    def get_available_etl_stacks(self) -> List[str]:
        results = self.db.query(models.SolarPanel.etl_stack_sequence).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_available_htl_stacks(self) -> List[str]:
        results = self.db.query(models.SolarPanel.htl_stack_sequence).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_available_backcontact_stacks(self) -> List[str]:
        results = self.db.query(models.SolarPanel.backcontact_stack_sequence).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_available_stability_protocols(self) -> List[str]:
        results = self.db.query(models.SolarPanel.stability_protocol).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_available_dimensions(self) -> List[str]:
        results = self.db.query(models.Perovskite.dimension).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_available_space_groups(self) -> List[str]:
        results = self.db.query(models.Perovskite.space_group).distinct().all()
        return [r[0] for r in results if r[0]]

    def get_perovskite_forms(self, form_type: str = "long", offset: int = 0, limit: int = 100) -> List[str]:
        if form_type == "short":
            query = self.db.query(models.Perovskite.composition_short_form)
        else:
            query = self.db.query(models.Perovskite.composition_long_form)

        results = query.distinct().offset(offset).limit(limit).all()
        return [r[0] for r in results if r[0]]
