from ast import literal_eval

from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder

from Models.series import PayloadSeries
from Models.payload import Payload
from Models.station import Station

from .utils.Requestor import Requestor


# GLOBALS
requestor = Requestor("ws://202.90.159.176:8080")
PAYLOAD_PARTITION = 6
PAYLOAD_UNIT = "m"
PAYLOAD_PLOTBANDS: list = []

app = FastAPI()


@app.get("/station/{station_type_id}/{station_id}")
def root(request: Request, station_type_id: int = 5, station_id: int = 987):

    if request.path_params["station_type_id"] != "5":
        raise HTTPException(
            status_code=404,
            detail=f"Station Type {request.path_params['station_type_id']} is not yet supported.",
        )
    if request.path_params["station_id"] != "987":
        raise HTTPException(
            status_code=404,
            detail=f"Station {request.path_params['station_id']} is not yet supported.",
        )

    station_info = Station(
        url=request.url.path,
        station_id=station_id,
        station_type_id=station_type_id,
        lat=9.0,
        lng=125.5167,
        verbose_name="Agusan River Entr, Butuan Bay",
    )

    if retrieve := requestor.retrieve(request.url.path):
        data = literal_eval(retrieve)

        rv_series = PayloadSeries(
            maxval=max(data["series"]["values"]),
            sensor_id=data["series"]["sensor_id"],
            label=data["series"]["label"],
            values=data["series"]["values"],
        )
        rv_time = data["time"]

    else:
        rv_series = PayloadSeries(maxval=-1.0, sensor_id=-1, label=-1, values=[])
        rv_time = []

    return jsonable_encoder(
        Payload(
            series=rv_series,
            plotbands=PAYLOAD_PLOTBANDS,
            station=station_info,
            time=rv_time,
            partition=PAYLOAD_PARTITION,
            unit=PAYLOAD_UNIT,
        )
    )
