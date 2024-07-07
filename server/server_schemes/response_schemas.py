from enum import Enum

from pydantic import BaseModel

class ResponseStatusEnum(str, Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    BAD_REQUEST = 'BAD_REQUEST'


class Response(BaseModel):
    status: ResponseStatusEnum
    message: str


class VideoMetadasResponse(Response):
    size_video: int

