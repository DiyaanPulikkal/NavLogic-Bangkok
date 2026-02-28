from pydantic import BaseModel


class QueryRequest(BaseModel):
    message: str


class RouteStep(BaseModel):
    type: str
    line: str | None = None
    board: str | None = None
    alight: str | None = None
    stations: list[str] | None = None
    # transfer fields
    from_station: str | None = None
    to_station: str | None = None


class RouteData(BaseModel):
    from_station: str
    to_station: str
    total_time: int
    steps: list[RouteStep]


class StationInfo(BaseModel):
    name: str
    lines: list[str]


class AttractionInfo(BaseModel):
    name: str
    station: str
