import socket

from pydantic import BaseModel


class BaseRequestSchema(BaseModel):

    def send_to_tcp_connection(self, connection:socket.socket):
        connection.sendall(self.model_dump_json().encode())

class BaseResponseSchema(BaseModel):

    @classmethod
    def from_tcp_connection(cls, connection: socket.socket):
        data = connection.recv(1024).decode('utf-8')
        return cls.model_validate_json(data)


class ClientSessionSchema(BaseRequestSchema):
    path_video: str
    udp_port: int
