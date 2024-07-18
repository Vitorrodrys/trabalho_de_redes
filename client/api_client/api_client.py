import bisect
from functools import reduce
import socket
import struct

from . import client_exceptions
from . import schemes

MTU_SIZE = 1500-20-8 # 1500 bytes (MTU size) - 20 bytes (IP header) - 8 bytes (UDP header)
MTU_VIDEO_BYTE_SIZE = MTU_SIZE - 4 - 4 # The first 4 bytes are the offset of the video frame and the second 4 bytes are the size of the video frame

class ApiClient:

    def __init__(
        self,
        server_address:str,
        server_port:int,
        wished_video:str
    ) -> None:

        self.__control_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__stream_socket.bind(("0.0.0.0", 0))
        self.__control_connection.connect(
            (server_address, server_port)
        )
        schemes.StartConnectionSchema(
            path_video=wished_video,
            udp_client_port=self.__stream_socket.getsockname()[1],
            udp_buffer_size=self.get_stream_sock_capacity()
        ).send_to_tcp_connection(self.__control_connection)

        response = schemes.VideoMetadasResponse.from_tcp_connection(self.__control_connection)
        if response.status in (schemes.ResponseStatusEnum.BAD_REQUEST, schemes.ResponseStatusEnum.ERROR):
            raise client_exceptions.VideoNotFoundException(wished_video)
        self.__video_meta_datas = response

    def get_video_meta_datas(self) -> schemes.VideoMetadasResponse:
        return self.__video_meta_datas.model_copy()

    def get_stream_sock_capacity(self)->int:
        return self.__stream_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

    def get_video_frame(
        self,
        offset: int,
        size: int
    )->bytes:
        sorted_bytes = []
        schemes.VideoBytesRequestSchema(
            offset=offset,
            length=size
        ).send_to_tcp_connection(self.__control_connection)
        response = schemes.Response.from_tcp_connection(self.__control_connection)
        if response.status == schemes.ResponseStatusEnum.BAD_REQUEST:
            raise ValueError(response.message)
        while True:
            data = self.__stream_socket.recv(MTU_SIZE)
            data = struct.unpack(f"ii{MTU_VIDEO_BYTE_SIZE}s", data)
            if data[0] == -1:
                break
            sorted_bytes.append(data)
        sorted_bytes.sort(key=lambda x: x[0])
        first_bytes = sorted_bytes[0]
        second_bytes = sorted_bytes[1]
        return reduce(
            lambda x, y: x + y[2][:y[1]], #lambda function to extract key from sorted bytes to apply reduce
            sorted_bytes[2:], #sorted bytes to apply reduce
            first_bytes[2][:first_bytes[1]] + second_bytes[2][:second_bytes[1]] #initial value of reduce
        )
