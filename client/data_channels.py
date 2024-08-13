import logging
from functools import reduce
import socket
import struct

from core import enviroment_settings, session_settings

EOF = b"#END#"

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
    def create_tcp_channel(
        cls,
        video_path: str,
        udp_port: int
    )->tuple["TCPChannel", int]:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect(
            (enviroment_settings.server_ip, enviroment_settings.server_port)
        )
        tcp_channel = cls(tcp_sock)
        tcp_channel.__write_data(f"{udp_port} {video_path}")
        return tcp_channel, int(tcp_channel.read_datas())

    def read_datas(self)->str:
        return self._sock.recv(
            1024
        ).decode('utf-8')

    def __write_data(self, data:str):
        data_bytes = data.encode('utf-8')
        if EOF in data_bytes:
            raise ValueError("data contains EOF")
        data_bytes += b' '+ EOF + b' '
        self._sock.send(
            data_bytes
        )

    def write_command(self, *args)->None:
        data = reduce(
            lambda x, y: str(x) + " " + str(y),
            args[1:],
            str(args[0])
        )
        self.__write_data(data)

class UDPChannel(BaseChannel):

    def __init__(self) -> None:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(("0.0.0.0", 0))
        udp_sock.settimeout(session_settings.udp_channel_timeout)
        super().__init__(udp_sock)

    def get_listening_udp_port(self)->int:
        return self._sock.getsockname()[1]

    def __deserialize(self, package: bytes)->tuple[int, bytes]:
        offset, data_length, datas = struct.unpack(f"ii{VIDEO_BYTES_SIZE}s", package)
        return offset, datas[0:data_length]

    def receive_frame(self)->bytes:
        frame = []
        while True:
            try:
                package = self._sock.recv(PACKAGE_MTU)
                offset, data = self.__deserialize(package)
                if offset == -1:
                    break
                frame.append((offset, data))
            except socket.timeout:
                logging.debug("a timeout ocurred while wait receive a strem package")
                break
        frame.sort(
            key=lambda x: x[0]
        )
        return reduce(
            lambda x, y: x + y[1],
            frame,
            b""
        )
