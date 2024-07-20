from enum import Enum

from .schemas import BaseResponseSchema

class ResponseStatusEnum(str, Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    BAD_REQUEST = 'BAD_REQUEST'

class Response(BaseResponseSchema):
    status: ResponseStatusEnum
    message: str

class VideoMetadasResponse(Response):
    size: int
