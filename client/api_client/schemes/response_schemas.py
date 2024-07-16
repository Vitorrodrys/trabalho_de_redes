from enum import Enum
import socket

from pydantic import BaseModel

class ResponseStatusEnum(str, Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    BAD_REQUEST = 'BAD_REQUEST'


class Response(BaseModel):
    @classmethod
    def from_tcp_connection(cls, connection: socket.socket):
        return cls.model_validate_json(connection.recv(1024).decode('utf-8'))
    status: ResponseStatusEnum
    message: str


class VideoMetadasResponse(Response):
    size: int
    bitrate:int

