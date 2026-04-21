from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import os

from ..components import AppComponents
from ..configuration import build_components
from ..entities.entities import PerovskiteDetailsRequest, PerovskiteDetailsResponse, SolarPanelResponse

router = APIRouter(prefix="/data", tags=["Data Management / CRUD"])


@router.post("/ingest")
def ingest_data(
        perovskites_path: str = Query("../data/enriched_perovskites.parquet"),
        solar_panels_path: str = Query("../data/solar_panels.parquet"),
        components: AppComponents = Depends(build_components)
):
    p_added, s_added = components.data_repository.ingest_from_parquet(perovskites_path, solar_panels_path)
    return {
        "message": "Ingestion complete",
        "perovskites_added": p_added,
        "solar_panels_added": s_added
    }


@router.get("/perovskites", response_model=List[PerovskiteDetailsResponse])
def get_perovskites(
        offset: int = 0,
        limit: int = 100,
        components: AppComponents = Depends(build_components)
):
    return components.data_repository.get_perovskites(offset=offset, limit=limit)


@router.get("/perovskite/{composition_long_form}", response_model=PerovskiteDetailsResponse)
def get_perovskite_details(
        composition_long_form: str,
        components: AppComponents = Depends(build_components)
):
    details = components.data_repository.get_perovskite_by_composition(composition_long_form)
    if not details:
        raise HTTPException(status_code=404, detail="Perovskite not found")
    return details


@router.get("/solar_panels", response_model=List[SolarPanelResponse])
def get_solar_panels(
        offset: int = 0,
        limit: int = 100,
        components: AppComponents = Depends(build_components)
):
    return components.data_repository.get_solar_panels(offset=offset, limit=limit)


@router.get("/etl_stacks", response_model=List[str])
def get_etl_stacks(components: AppComponents = Depends(build_components)):
    return components.data_repository.get_available_etl_stacks()


@router.get("/htl_stacks", response_model=List[str])
def get_htl_stacks(components: AppComponents = Depends(build_components)):
    return components.data_repository.get_available_htl_stacks()


@router.get("/backcontact_stacks", response_model=List[str])
def get_backcontact_stacks(components: AppComponents = Depends(build_components)):
    return components.data_repository.get_available_backcontact_stacks()


@router.get("/stability_protocols", response_model=List[str])
def get_stability_protocols(components: AppComponents = Depends(build_components)):
    return components.data_repository.get_available_stability_protocols()


@router.get("/dimensions", response_model=List[str])
def get_dimensions(components: AppComponents = Depends(build_components)):
    return components.data_repository.get_available_dimensions()


@router.get("/space_groups", response_model=List[str])
def get_space_groups(components: AppComponents = Depends(build_components)):
    return components.data_repository.get_available_space_groups()


@router.get("/perovskite_forms", response_model=List[str])
def get_perovskite_forms(
        form_type: str = Query("long", enum=["long", "short"]),
        offset: int = 0,
        limit: int = 100,
        components: AppComponents = Depends(build_components)
):
    return components.data_repository.get_perovskite_forms(form_type=form_type, offset=offset, limit=limit)
