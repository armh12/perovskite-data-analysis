from fastapi import APIRouter, Depends
from ..components import AppComponents
from ..configuration import build_components
from ..entities.entities import (
    BandGapDiscoveryRequest, BandGapDiscoveryResponse,
    SolarPanelDiscoveryRequest, SolarPanelDiscoveryResponse
)
from ..services.discovery_service import search_optimal_band_gap, search_optimal_solar_panel

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/band_gap", response_model=BandGapDiscoveryResponse)
async def search_band_gap(
        request: BandGapDiscoveryRequest,
        components: AppComponents = Depends(build_components)
):
    """Search for the best perovskite composition targeting a specific Band Gap."""
    return search_optimal_band_gap(request, components)


@router.post("/solar_panel", response_model=SolarPanelDiscoveryResponse)
async def search_solar_panel(
        request: SolarPanelDiscoveryRequest,
        components: AppComponents = Depends(build_components)
):
    """Search for the best overall solar panel configuration targeting a specific Stability (T80)."""
    return search_optimal_solar_panel(request, components)
