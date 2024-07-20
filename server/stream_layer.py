import os
import socket
import struct
from threading import Thread, Lock, Event

from core.settings import environment_settings

class StreamError(Exception):
    pass

class VideoNotFoundError(StreamError, FileNotFoundError):
    pass

class InvalidSeekPositionError(StreamError):
    def __init__(self, seek_position: int):
        self.seek_position = seek_position
        super().__init__(f"Invalid seek position: {seek_position}")


CHUNK_SIZE = 4096
MTU = 1500-20-8 #1500 bytes (MTU size) - 20 bytes (IP header) - 8 bytes (UDP header)
MTU_VIDEO_BYTE_SIZE = MTU-4-4 # MTU - 4 bytes (integer offset size) - 4 bytes (integer data length)


class StreamLayer:

    @classmethod
    def __serialize_data(cls, offset: int, video_bytes: bytes):
        struct_format = f"ii{MTU_VIDEO_BYTE_SIZE}s"
        return struct.pack(struct_format, offset, len(video_bytes), video_bytes)

    def __send_packages(self, current_offset:int, frame: bytes):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(0, len(frame), MTU_VIDEO_BYTE_SIZE):
            serialized_datas = self.__serialize_data(current_offset+i, frame[i:i+MTU_VIDEO_BYTE_SIZE])
            udp_socket.sendto(
                serialized_datas,
                (self.__client_address, self.__udp_port)
            )
    def __send_video_frames(self):
        size_read_in_each_iteration = CHUNK_SIZE*environment_settings.block_size_sended_per_iteration
        while not self.__kill.is_set():
            with self.__lock:
                self.__pause.acquire()
                self.__pause.release()
                frame = self.__file.read(size_read_in_each_iteration)
                self.__send_packages(
                    self.__current_offset,
                    frame
                )
                self.__current_offset += size_read_in_each_iteration

    @classmethod
    def __open_video(self, video_filename:str, *args, **kw):
        if not os.path.exists(video_filename):
            raise VideoNotFoundError(f"Video {video_filename} not found")
        file = open(video_filename, "rb", *args, **kw)
        yield file
        file.close()

    def __init__(
        self,
        path_video: str,
        udp_port: int,
        client_address: str
    ) -> None:
        self.__file = next(self.__open_video(path_video))
        self.__path_video = path_video
        self.__udp_port = udp_port
        self.__client_address = client_address
        self.__lock = Lock()
        self.__pause = Lock()
        self.__kill = Event()
        self.__current_offset = 0
        self.__stream_worker_thread = Thread(
            target=self.__send_video_frames,
            daemon=True
        )
        self.__stream_worker_thread.start()

    def pause(self):
        with self.__lock:
            if self.__pause.locked():
                self.__pause.release()
                return False
            self.__pause.acquire()
            return True

    def stop(self):
        with self.__lock:
            self.__kill.set()
            self.__pause.release()
        self.__stream_worker_thread.join()

    def seek(self, position:int):
        if position < 0:
            raise InvalidSeekPositionError(position)
        if position >= os.path.getsize(self.__path_video):
            raise InvalidSeekPositionError(position)
        with self.__lock:
            self.__file.seek(position)
            self.__current_offset = position
