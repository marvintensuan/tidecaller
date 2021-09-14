from pydantic import BaseModel
from typing import Optional

from .station import Station
from .series import PayloadSeries


class Payload(BaseModel):
    series: PayloadSeries
    plotbands: Optional[list]
    station: Station
    time: list
    partition: int
    unit: str
