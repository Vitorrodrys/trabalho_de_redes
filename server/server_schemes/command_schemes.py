from abc import ABC, abstractmethod
from typing import Union, Literal

from stream_layer import StreamLayer

from .schemas import RequestSchema

class StopConnection(Exception):
    pass

class BaseCommand(RequestSchema, ABC):
    @abstractmethod
    def execute(self, stream_layer: StreamLayer):
        pass

class PauseCommand(BaseCommand):
    pause: Literal[True]

    def execute(self, stream_layer: StreamLayer):
        return stream_layer.pause()

class StopCommand(BaseCommand):
    stop: Literal[True]

    def execute(self, stream_layer: StreamLayer):
        stream_layer.stop()
        raise StopConnection()

class SeekCommand(BaseCommand):
    seek: int

    def execute(self, stream_layer: StreamLayer):
        return stream_layer.seek(self.seek)

class SomeCommand(RequestSchema):
    command: Union[PauseCommand, StopCommand, SeekCommand]
