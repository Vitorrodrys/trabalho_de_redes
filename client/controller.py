from threading import Thread, Lock

from api_client import ApiClient
from client.core.settings import environment_settings
from video_buffer import Buffer


class Controller:

    def __receive_video(self):
        video_metadadas = self.__api_client.get_video_meta_datas()
        frame_size = int(video_metadadas.bitrate/2)
        while self.__current_offset + video_metadadas.bitrate < video_metadadas.size:
            if self.__buffer.get_buffer_size() > int(video_metadadas.size*0.5+1):
                continue
            with self.__lock:
                frame = self.__api_client.get_video_frame(
                    offset=self.__current_offset,
                    size=frame_size
                )
                self.__buffer.add_video_frame(frame)
                self.__current_offset += frame_size
    def __init__(
        self,
        wished_video: str
    ) -> None:
        self.__api_client = ApiClient(
            server_address=environment_settings.server_address,
            server_port=environment_settings.server_port,
            wished_video=wished_video
        )
        self.__buffer = Buffer()
        self.__lock = Lock()
        self.__current_offset = 0
        self.__updater_thread = Thread(
            target=self.__receive_video
        )
        self.__updater_thread.start()

    def seek_video(self, percentage: float):
        if percentage > 1 or percentage < 0:
            raise ValueError("percentage should be between 0 and 1")
        with self.__lock:
            self.__current_offset = int(
                self.__api_client.get_video_meta_datas().size*percentage
            )
            self.__buffer.clear_buffer()

    def pause(self):
        with self.__lock:
            self.__buffer.pause()
