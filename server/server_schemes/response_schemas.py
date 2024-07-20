from enum import Enum
import os

from .schemas import ResponseSchema

class ResponseStatusEnum(str, Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    BAD_REQUEST = 'BAD_REQUEST'


class Response(ResponseSchema):
    status: ResponseStatusEnum
    message: str = "command executed successfully"

class VideoMetadasResponse(Response):
    size: int

    @classmethod
    def from_path_video(cls, path_video:str):
        size = os.path.getsize(path_video)
        return cls(
            status=ResponseStatusEnum.OK,
            message="Video metadas",
            size=size
        )
