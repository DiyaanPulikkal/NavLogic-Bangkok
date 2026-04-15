from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/stations")
async def list_stations(request: Request):
    """Grouped by station name, each with the list of lines it serves."""
    prolog = request.app.state.orchestrator.prolog
    return prolog.get_stations_with_lines()


@router.get("/attractions")
async def list_attractions(request: Request):
    """All tagged POIs — name, nearest station, and tag list."""
    prolog = request.app.state.orchestrator.prolog
    return prolog.get_all_pois()
