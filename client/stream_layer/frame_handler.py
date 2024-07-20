from functools import reduce
import struct

from core import environment_settings, network_settings

class FrameHandler:

    def __deserialize_data(self, video_bytes: bytes)->tuple[int, bytes]:
        struct_format = f"ii{network_settings.mtu_video_byte_size}s"
        t = struct.unpack(struct_format, video_bytes)
        return t[0], t[2][:t[1]]
    def __init__(
        self,
        mpv_frames_size: int = environment_settings.mpv_frames_size
    ) -> None:
        self.__mpv_frames_size = mpv_frames_size
        self.__frame = []

    def insert_new_package(self, package:bytes):
        desirialized_datas = self.__deserialize_data(package)
        self.__frame.append(desirialized_datas)

    def get_next_frame(self) -> bytes:
        if len(self.__frame) < self.__mpv_frames_size:
            return None
        self.__frame.sort(key=lambda x: x[0])
        reduced_frame = reduce(
            lambda x, y: (x + y[1]),
            self.__frame[2:],
            self.__frame[0][1] + self.__frame[1][1]
        )
        self.__frame = []
        return reduced_frame
    def seek(self):
        self.__frame = []
    def stop(self):
        self.__frame = []
