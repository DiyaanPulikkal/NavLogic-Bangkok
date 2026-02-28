from fastapi import APIRouter, Query, Request

router = APIRouter()


@router.get("/route")
async def get_route(
    request: Request,
    start: str = Query(..., description="Starting location"),
    end: str = Query(..., description="Destination location"),
):
    orchestrator = request.app.state.orchestrator
    result = orchestrator.find_route(start, end)
    return result
