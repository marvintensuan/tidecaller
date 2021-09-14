from pydantic import BaseModel
from typing import Optional


class PayloadSeries(BaseModel):
    maxval: float
    sensor_id: int
    label: int
    values: list
