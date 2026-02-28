from fastapi import APIRouter, Request
from api.schemas import QueryRequest

router = APIRouter()


@router.post("/query")
async def query(body: QueryRequest, request: Request):
    orchestrator = request.app.state.orchestrator
    result = orchestrator.handle(body.message)
    return result
