from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine import Orchestrator
from engine.config import setup_logging
from db.database import engine, Base
from api.routes.query import router as query_router
from api.routes.route import router as route_router
from api.routes.stations import router as stations_router
from api.routes.auth import router as auth_router
from api.routes.conversations import router as conversations_router
from api.routes.schedule import router as schedule_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Base.metadata.create_all(bind=engine)
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

app.include_router(auth_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(route_router, prefix="/api")
app.include_router(stations_router, prefix="/api")
app.include_router(schedule_router, prefix="/api")
