# Tidecaller: Recreating Project Noah's Websocket Request caller using FastAPI

This repository is available [here](https://github.com/marvintensuan/tidecaller).

## About

This is a prototype web server designed with the following purpose in mind:

1. To debug the root cause of Project Noah's sensors API errors from an outsider's perpective.
2. Propose a new application logic while preserving Project Noah's existing schema. 
3. Do all of the above using a modern web framework.

We have chosen FastAPI to create a sample API endpoint which can handle the diagnosed cause of Internal Server Errors.

Once again, this app is a prototype and is never meant to be deployed to production. Nevertheless, FastAPI is a sturdy web framework and is used by the world's biggest tech companies in their internal processes.


## Problem Statement

A good data pipeline starts with a good data collection process. 

Project Noah shows that Butuan City has one tide sensor and one rain sensor. However, Project Noah's sensor data comes problems; one of which is that ***sensors are rarely available*** due to `UnboundLocalError`.

Over the course of the Hackathon (and our availability), Project Noah's sensors data has only worked a total of two times. Fortunately, those are enough times to investigate and diagnose the problem.

The website is also written in Python 2.7 using Tornado 3.2. *For reference, Python is currently on version 3.9 and Tornado is on 6.1 at the time of this writing.*

## Data Gathered

- Of the two sensors, only the Tide sensor contains data.
- To display all sensors available, Project Noah's website frontend calls the URL `http://noah.up.edu.ph/sensors/all`. This endpoint works most of the time.
- To display all available tide sensors, the website frontend calls the URL `http://noah.up.edu.ph/sensors/tide`. This endpoint does <u>**not**</u> work most of the time.

During down times, the website instead sends a traceback such as below:

```
Connection: keep-alive
Content-Length: 1205
Content-Type: text/plain
Date: Sun, 12 Sep 2021 04:03:53 GMT
Server: TornadoServer/3.2

Traceback (most recent call last):
  File "/usr/local/lib/python2.7/dist-packages/tornado/web.py", line 1192, in _stack_context_handle_exception
    raise_exc_info((type, value, traceback))
  File "/usr/local/lib/python2.7/dist-packages/tornado/stack_context.py", line 302, in wrapped
    ret = fn(*args, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/tornado/web.py", line 1384, in future_complete
    f.result()
  File "/usr/local/lib/python2.7/dist-packages/tornado/concurrent.py", line 129, in result
    raise_exc_info(self.__exc_info)
  File "/usr/local/lib/python2.7/dist-packages/tornado/stack_context.py", line 302, in wrapped
    ret = fn(*args, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/tornado/gen.py", line 574, in inner
    self.set_result(key, result)
  File "/usr/local/lib/python2.7/dist-packages/tornado/gen.py", line 500, in set_result
    self.run()
  File "/usr/local/lib/python2.7/dist-packages/tornado/gen.py", line 531, in run
    yielded = self.gen.send(next)
  File "/home/noah/noah-frontend-server/sensors/sensor_handler.py", line 73, in get
    self.write(json.dumps(response))
UnboundLocalError: local variable 'response' referenced before assignment
```

- To view data from specific sensor (e.g. Butuan City's Tide sensor), the website establishes a connection to the websocket `ws://202.90.159.176:8080/station/5/987` where:
    - `5` is the sensor type ID (tide); and
    - `987` is the location ID (Butuan City).
- The data obtained from the websocket is in the form of `byte` string, a sample of which is in the [sample_response.txt](https://github.com/marvintensuan/tidecaller/blob/master/sample_response.txt).

## Methodology

I have developed a web application using FastAPI to simulate the endpoint in question.

FastaPI is one of the fastest Python web framework in the market while maintaining simple syntax similar to Flask. These are the key reasons why I chose the framework over rewriting a Tornado clone. This is also going to come in handy when *active maintenance* of the app/feature is out of the question.

The app architecture is as follows:

```
app\
    main.py
    utils\
        PathParamsValidator.py
        Requestor.py
Models\
    payload.py
    series.py
    station.py
Dockerfile
pyproject.toml
requirements.txt
```

### Installation

This app comes with a `pyproject.toml`. Simply type `poetry install` when using poetry.

This project also comes with a `requirements.txt` file so users can also opt to install via pip. To install via pip, input `pip install -r requirements.txt` on your terminal.

Regardless of the method preferred, ensure that your terminal is in the correct working directory.

### How to use

To use this app, simply type below commands on the terminal:

```
uvicorn app.main:app
```

A web application should now start serving the application (in debug mode). Your terminal should then look like this:

```
INFO:     Started server proces [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

To use the app, you need to send a request, either via command line or via browser. Personally, I used `httpie` via commandline.

```bash
>>> http GET 127.0.0.1:8000/station/5/987

HTTP/1.1 200 OK
content-length: 258
content-type: application/json
date: Sun, 12 Sep 2021 12:56:12 GMT
server: uvicorn

{
    "partition": 6,
    "plotbands": [],
    "series": {
        "label": -1,
        "maxval": -1.0,
        "sensor_id": -1,
        "values": []
    },
    "station": {
        "lat": 9.0,
        "lng": 125.5167,
        "station_id": 987,
        "station_type_id": 5,
        "url": "/station/5/987",
        "verbose_name": "Agusan River Entr, Butuan Bay"
    },
    "time": [],
    "unit": "m"
}
```

## Lessons Learned

After recreating a mock of Project Noah's API enpoints, we can infer that the backend most probably follows the pattern below:

```python
import json

import tornado.web

class MainHandler(tornado.web.RequestHandler):
    '''Adapted from Tornado docs'''
    def get(self):
        data = get_data_from_websocket()  # Retrieve from websocket
        
        if data:
            response = do_something()
        
        self.write(json.dumps(response))  # Refer to the traceback above
```

In this particular example, the variable `data` is dependent on the websocket. If the websocket fails, it gives `data` a falsy value and hence, `response` exists but is not initialized, raising an `UnboundLocalError`. 

- Requesting data from the websocket is done via the `Requestor` class.
- FastAPI's support for Object-Oriented Programming also came in handy. The `Payload` and parts of the Payload are all Pydantic classes.
- Built-in support for types and error handling is also a welcome addition.


```bash
>>> http GET http://127.0.0.1:8000/all
HTTP/1.1 404 Not Found
content-length: 22
content-type: application/json
date: Sun, 12 Sep 2021 09:29:03 GMT
server: uvicorn

{
    "detail": "Not Found"
}

>>> http GET http://127.0.0.1:8000/station/tide/987
HTTP/1.1 422 Unprocessable Entity
content-length: 112
content-type: application/json
date: Sun, 12 Sep 2021 09:30:42 GMT
server: uvicorn

{
    "detail": [
        {
            "loc": [
                "path",
                "station_type_id"
            ],
            "msg": "value is not a valid integer",
            "type": "type_error.integer"
        }
    ]
}
```
These provides a much cleaner data for the frontend to handle, and is definitely an upgrade over sending tracebacks.

## Future Recommendations

This web app only focused on one endpoint: `/station/5/987`. However, it has the potential to be scaled to all endpoints available in Project Noah, including but not limited to:

- `sensors/all` &mdash; list of all available sensors and description.
- other sensor types (e.g. rain, stream, weather)
- other locations

Connection to *the* actual database will also prove to be useful.

This prototype also does not provide proper tests. Although static type checker, `mypy`, is part of this project's dev dependencies.

Lastly, FastAPI is a modern web framework that provides value even with minimum maintenance. It is highly encouraged to assess the feasibility of completely refactoring the whole code base.