from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException


class Requestor:
    """Websocket request handler."""

    def __init__(self, URI: str = "") -> None:
        self.URI = URI
        self.__bool__ = False

    def retrieve(self, path: str) -> bytes:
        try:
            ws = create_connection("".join([self.URI, path]))
            response = ws.recv_data_frame()
            return response[1].data
        except WebSocketConnectionClosedException:
            return b""
