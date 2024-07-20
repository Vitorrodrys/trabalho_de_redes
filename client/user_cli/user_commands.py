from abc import ABC, abstractmethod

from api_client import ApiClient, schemes

class UserCommand(ABC):

    def __init__(
        self,
        api_client: ApiClient,
        video_metadatas: schemes.VideoMetadasResponse
    ) -> None:
        self._api_client = api_client
        self._video_metadatas = video_metadatas

    @abstractmethod
    def execute(self):
        pass

class PauseCommand(UserCommand):

    def execute(self):
        self._api_client.pause()

class SeekCommand(UserCommand):

    def execute(self):
        position = int(input("Enter the position: "))
        self._api_client.seek(position)

class StopCommand(UserCommand):

    def execute(self):
        self._api_client.stop()
