from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/stations")
async def list_stations(request: Request):
    orchestrator = request.app.state.orchestrator
    return orchestrator.get_all_stations_with_lines()


@router.get("/attractions")
async def list_attractions(request: Request):
    orchestrator = request.app.state.orchestrator
    return orchestrator.get_all_attractions()
