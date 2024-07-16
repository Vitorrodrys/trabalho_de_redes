import os
from socket import socket

from enum import Enum

from pydantic import BaseModel
from pymediainfo import MediaInfo
class ResponseStatusEnum(str, Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    BAD_REQUEST = 'BAD_REQUEST'


class Response(BaseModel):
    status: ResponseStatusEnum
    message: str

    def send_to_tcp_connection(self, connection:socket):
        connection.sendall(self.model_dump_json().encode())

class VideoMetadasResponse(Response):
    size: int
    bitrate: int

    @classmethod
    def from_path_video(cls, path_video:str):
        def get_bitrate(media_info:MediaInfo):
            for track in media_info.tracks:
                if track.track_type == 'Video':
                    return track.bit_rate
            raise ValueError(f'bitrate not found to video "{path_video}"')
        bitrate = get_bitrate(MediaInfo.parse(path_video))
        size = os.path.getsize(path_video)
        return cls(
            status=ResponseStatusEnum.OK,
            message="Video metadas",
            size=size,
            bitrate=bitrate
        )
