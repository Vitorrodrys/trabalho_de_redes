import subprocess
from threading import Event, Thread

from data_channels import UDPChannel

from .client_api import StreamAPI


class StreamLayer:

    @classmethod
    def create_mpv_pipe(cls):
        mpv_command = [
            "mpv",
            "--no-cache",
            "--cache=no",
            "--quiet",
            "--no-terminal",
            "--input-conf=/dev/null",
            "-"
        ]
        return subprocess.Popen(
            mpv_command,
            stdin=subprocess.PIPE
        )
    def __worker_method(self):
        mpv_pipe = self.create_mpv_pipe()
        while self.__kill_event.is_set() is False:
            self.__stream_api.request_a_video_package()
            video_package = self.__udp_channel.receive_frame()
            self.__stream_api.send_feedback(len(video_package))
            mpv_pipe.stdin.write(video_package)
            #mpv_pipe.stdin.flush()
    def __init__(
        self,
        stream_api: StreamAPI,
        udp_channel: UDPChannel
    ) -> None:
        self.__stream_api = stream_api
        self.__udp_channel = udp_channel
        self.__worker_thread = Thread(target=self.__worker_method)
        self.__worker_thread.start()
        self.__kill_event = Event()

    def stop(self):
        self.__kill_event.set()
        self.__worker_thread.join()
        self.__udp_channel.close()
