import subprocess
from threading import Thread
from threading import Lock
import time


class Buffer:

    def __feeds_the_video_player(self, mpv_pipe:subprocess.Popen):
        while True:
            time.sleep(1)

            with self.__pause:
                pass
            with self.__lock:
                if not self.__video_buffer:
                    continue
                new_bytes = self.__video_buffer.pop(0)
                mpv_pipe.stdin.write(new_bytes)
                self.__buffer_size -= len(new_bytes)
                mpv_pipe.stdin.flush()

    def __start_handler_video_player(self):
        if self.__handler_video_player and self.__handler_video_player.is_alive():
            return
        mpv_command = [
            "mpv",
            "--no-cache",
            "--cache=no",
            "--quiet",
            "--no-terminal",
            "--input-conf=/dev/null",
            "-"
        ]
        mpv_pipe = subprocess.Popen(mpv_command, stdin=subprocess.PIPE)
        self.__handler_video_player = Thread(
            target=self.__feeds_the_video_player,
            args=(mpv_pipe,)
        )
        self.__handler_video_player.start()

    def add_video_frame(self, video_frame:bytes):
        with self.__lock:
            self.__video_buffer.append(video_frame)
            self.__buffer_size += len(video_frame)
    def clear_buffer(self):
        with self.__lock:
            self.__video_buffer = []
            self.__buffer_size = 0
    def pause(self):
        if self.__pause.locked():
            self.__pause.release()
            return
        self.__pause.acquire()
    def get_buffer_size(self):
        with self.__lock:
            return self.__buffer_size
    def __init__(self) -> None:
        self.__handler_video_player: Thread = None
        self.__lock = Lock()
        self.__pause = Lock()
        self.__video_buffer = []
        self.__buffer_size = 0
        self.__start_handler_video_player()
        