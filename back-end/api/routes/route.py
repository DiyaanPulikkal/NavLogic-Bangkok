from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter()


@router.get("/route")
async def get_route(
    request: Request,
    start: str = Query(..., description="Starting station or POI name"),
    end: str = Query(..., description="Destination station or POI name"),
):
    """Pure point-to-point routing — no LLM, no theme filtering.

    Returns `{"type": "plan", "data": {origin, destination, total_time, steps}}`
    on success, or `{"type": "error", "data": {"message": ...}}` on bad input.
    """
    orchestrator = request.app.state.orchestrator
    result = orchestrator.handle_pure_route(start, end)
    if result["type"] == "error":
        raise HTTPException(status_code=404, detail=result["data"]["message"])
    return result
