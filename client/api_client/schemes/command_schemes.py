from socket import socket

from .schemas import BaseRequestSchema
class Command(BaseRequestSchema):
    def send_to_tcp_connection(self, connection:socket):
        __WrapperCommand(
            command=self
        ).send_to_tcp_connection(connection)
class __WrapperCommand(BaseRequestSchema):
    command: Command

class PauseCommand(Command):
    pause: bool = True

class SeekCommand(Command):
    position: int

class StopCommand(Command):
    stop: bool = True
