from pydantic import BaseModel


class VideoBytesRequestSchema(BaseModel):
    offset: int
    length: int
