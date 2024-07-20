import socket

from pydantic import BaseModel


class RequestSchema(BaseModel):
    @classmethod
    def from_tcp_connection(cls, connection: socket.socket):
        return cls.model_validate_json(connection.recv(1024).decode('utf-8'))

class ResponseSchema(BaseModel):
    def send_to_tcp_connection(self, connection:socket.socket):
        connection.sendall(self.model_dump_json().encode())

class SessionConnectionSchema(RequestSchema):
    path_video: str
    udp_port: int
