from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine import Orchestrator
from engine.config import setup_logging
from api.routes.query import router as query_router
from api.routes.route import router as route_router
from api.routes.stations import router as stations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app.state.orchestrator = Orchestrator()
    yield


app = FastAPI(
    title="Bangkok Public Transport API",
    description="Query Bangkok's public transit network — routes, stations, and attractions.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router, prefix="/api")
app.include_router(route_router, prefix="/api")
app.include_router(stations_router, prefix="/api")
