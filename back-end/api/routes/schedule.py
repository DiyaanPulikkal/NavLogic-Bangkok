from fastapi import APIRouter, Request, Query

router = APIRouter()


@router.get("/schedule")
async def schedule(
    request: Request,
    origin: str = Query(..., description="Starting station or attraction name"),
    destination: str = Query(..., description="Destination station or attraction name"),
    deadline: str = Query("09:00", description="Latest arrival time in HH:MM format"),
):
    """Plan a time-constrained trip using the transit schedule.

    Uses First-Order Logic facts, Unification, and Proof by Resolution
    in the Prolog engine to find valid itineraries.
    """
    orchestrator = request.app.state.orchestrator
    return orchestrator.plan_trip(origin, destination, deadline)
