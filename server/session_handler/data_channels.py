import socket
import struct
import typing

from core import server_settings, session_settings

IP_HEADER_SIZE = 20
UDP_HEADER_SIZE = 8
PACKAGE_MTU = session_settings.network_mtu - IP_HEADER_SIZE - UDP_HEADER_SIZE

OFFSET_HEADER_SIZE = 4
DATA_LENGTH_HEADER_SIZE = 4
VIDEO_BYTES_SIZE = PACKAGE_MTU - OFFSET_HEADER_SIZE - DATA_LENGTH_HEADER_SIZE


class BaseChannel:
    def __init__(
        self,
        sock: socket.socket
    ) -> None:
        self._sock = sock

    def close(self):
        self._sock.close()

class TCPChannel(BaseChannel):

    @classmethod
    def create_tcp_socket(
        cls,
        ip_listen:str,
        port: int,
        *,
        max_connections: typing.Optional[int] = server_settings.max_connections,
        default_timeout: typing.Optional[float] = session_settings.default_timeout
    )->socket.socket:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip_listen, port))
        server_socket.listen(max_connections)
        if not default_timeout:
            raise ValueError("Invalid timeout value")
        server_socket.settimeout(default_timeout)
        return server_socket

    def read_datas(self)->tuple[str]:
        return tuple(
            self._sock.recv(
                1024
            ).decode('utf-8').split(' ')
        )

    def write_data(self, data: str)->None:
        self._sock.send(
            data.encode('utf-8')
        )

class UDPChannel(BaseChannel):

    def __init__(
        self,
        client_address: str,
        client_port: int
    ) -> None:
        self.__client_address = client_address
        self.__client_port = client_port
        super().__init__(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        )

    @classmethod
    def __serialize_bytes(cls, video_package: bytes, offset: int)->bytes:
        return struct.pack(
            f"!II{VIDEO_BYTES_SIZE}s",
            offset,
            len(video_package),
            video_package
        )

    def send_data(self, data:bytes):
        for index in range(0, len(data), VIDEO_BYTES_SIZE):
            package = self.__serialize_bytes(data[index:index+VIDEO_BYTES_SIZE], index)
            self._sock.sendto(
                package,
                (self.__client_address, self.__client_port)
            )
        self._sock.sendto(
            self.__serialize_bytes(
                bytes("-1"),
                -1
            )
        )
