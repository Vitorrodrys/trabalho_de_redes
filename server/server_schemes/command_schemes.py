from enum import Enum
import socket
from typing import Iterator

from pydantic import BaseModel


CHUNK_SIZE = 4096


class BaseCommand(BaseModel):

    @classmethod
    def from_tcp_connection(cls, connection: socket.socket):
        return cls.model_validate_json(connection.recv(1024).decode('utf-8'))

class StartConnectionSchema(BaseCommand):
    path_video: str
    udp_client_port: int
    udp_buffer_size: int

class FrameRequestSchema(BaseCommand):
    offset: int
    length: int

    def reader_iterator(self) -> Iterator[int]:
        first_quantity = CHUNK_SIZE * int(self.length/CHUNK_SIZE)
        second_quantity = self.length - first_quantity
        yield first_quantity
        yield second_quantity


class SendStatusEnum(str, Enum):
    ok_continue = 'OK_CONTINUE'
    stop = 'STOP'
class SendStatusSchema(BaseCommand):
    status: SendStatusEnum
