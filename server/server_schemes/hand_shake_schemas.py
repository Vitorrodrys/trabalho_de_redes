from pydantic import BaseModel


class StartConnectionSchema(BaseModel):
    path_video: str
    udp_client_port: int

    