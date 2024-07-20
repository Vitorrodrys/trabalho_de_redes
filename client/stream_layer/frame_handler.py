import struct
from threading import Lock

from core import environment_settings, network_settings

class FrameHandler:

    def __deserialize_data(self, video_bytes: bytes)->tuple[int, bytes]:
        struct_format = f"ii{network_settings.mtu_video_byte_size}s"
        t = struct.unpack(struct_format, video_bytes)
        return t[0], t[2][:t[1]]
    def __init__(
        self,
        max_wait_buffer_size: int = environment_settings.max_wait_buffer_size
    ) -> None:
        self.__max_wait_buffer_size = max_wait_buffer_size
        self.__wait_buffer_size: dict[int, bytes] = {}
        self.__current_offset = 0
        self.__lock = Lock()

    def get_next_frame(self, new_frame: bytes):
        offset, frame_bytes = self.__deserialize_data(new_frame)
        with self.__lock:
            if offset == self.__current_offset:
                self.__current_offset += len(frame_bytes)
                return frame_bytes
            if offset < self.__current_offset:
                return None
            self.__wait_buffer_size[offset] = frame_bytes
            if len(self.__wait_buffer_size) > self.__max_wait_buffer_size:
                offset, frame_bytes = self.__wait_buffer_size.pop(
                    min(self.__wait_buffer_size.keys())
                )
                self.__current_offset = offset
                return frame_bytes
