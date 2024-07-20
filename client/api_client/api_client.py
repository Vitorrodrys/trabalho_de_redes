import socket

from stream_layer import StreamLayer

from . import client_exceptions
from . import schemes

class ApiClient:

    @classmethod
    def create_session(
        cls,
        server_address:str,
        server_port:int,
        wished_video:str
    ):
        control_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_connection.connect(
            (server_address, server_port)
        )
        stream_layer = StreamLayer()
        schemes.ClientSessionSchema(
            path_video=wished_video,
            udp_port=stream_layer.get_listening_udp_port()
        ).send_to_tcp_connection(control_connection)

        response = schemes.VideoMetadasResponse.from_tcp_connection(control_connection)
        if response.status in (
            schemes.ResponseStatusEnum.BAD_REQUEST,
            schemes.ResponseStatusEnum.ERROR
        ):
            raise client_exceptions.VideoNotFoundException(wished_video)
        return cls(control_connection, stream_layer), response

    def __init__(
        self,
        control_connection: socket.socket,
        stream_layer: StreamLayer
    ) -> None:

        self.__control_connection = control_connection
        self.__stream_layer = stream_layer

    def pause(self):
        schemes.PauseCommand().send_to_tcp_connection(self.__control_connection)

    def stop(self):
        self.__stream_layer.stop()
        schemes.StopCommand().send_to_tcp_connection(self.__control_connection)


    def seek(self, position:int):
        self.__stream_layer.seek(position)
        schemes.SeekCommand(position=position).send_to_tcp_connection(self.__control_connection)
        response = schemes.Response.from_tcp_connection(self.__control_connection)
        if response.status != schemes.ResponseStatusEnum.OK:
            raise client_exceptions.InvalidSeekPosition(response.message)
