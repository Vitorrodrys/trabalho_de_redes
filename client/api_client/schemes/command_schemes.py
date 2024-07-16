from socket import socket

from enum import Enum

from pydantic import BaseModel


class Command(BaseModel):
    def send_to_tcp_connection(self, connection:socket):
        connection.sendall(self.model_dump_json().encode())

class StartConnectionSchema(Command):
    path_video: str
    udp_client_port: int
    udp_buffer_size: int

class VideoBytesRequestSchema(Command):
    offset: int
    length: int

class SendStatusEnum(str, Enum):
    ok_continue = 'OK_CONTINUE'
    stop = 'STOP'
class SendStatusSchema(Command):
    status: SendStatusEnum
