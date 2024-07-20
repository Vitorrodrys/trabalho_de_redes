import socket
import subprocess
from threading import Event, Thread

from core import network_settings
from client.stream_layer.frame_handler import FrameHandler

class StreamLayer:

    def __feeds_the_video_player(self, mpv_pipe:subprocess.Popen):
        while not self.__kill.is_set():
            data = self.__udp_socket.recv(network_settings.mtu)
            next_frame = self.__frame_handler.get_next_frame(data)
            if next_frame:
                mpv_pipe.stdin.write(next_frame)
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

    def __init__(self):
        self.__udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__udp_socket.bind(("0.0.0.0", 0))
        self.__kill = Event()
        self.__handler_video_player: Thread = None
        self.__frame_handler = FrameHandler()
        self.__start_handler_video_player()

    def get_listening_udp_port(self):
        return self.__udp_socket.getsockname()[1]
