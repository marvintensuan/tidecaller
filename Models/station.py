from pydantic import BaseModel


class Station(BaseModel):
    url: str
    station_id: int
    station_type_id: int
    lat: float
    lng: float
    verbose_name: str
