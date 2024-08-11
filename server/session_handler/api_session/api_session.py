from data_channels import TCPChannel

from .command_registry import CommandRegistry
from .stream_layer import RequestFrame, StreamLayer
from .window_handler import WindowHandler


commands_registry = CommandRegistry()

class StopSession(Exception):
    pass

class APISession:

    def __init__(
        self,
        tcp_channel: TCPChannel,
        stream_layer: StreamLayer
    ) -> None:
        self.__tcp_channel = tcp_channel
        self.__window_handler = WindowHandler()
        self.__stream_layer = stream_layer

    @commands_registry.add("get_video_frame")
    def request_a_video_package(self):
        package_size = self.__window_handler.get_window_size()
        self.__stream_layer.add_request(RequestFrame(package_size))

    @commands_registry.add("feedback")
    def receive_client_feedback(self, received_packages: int):
        self.__window_handler.update_window_size(received_packages)

    @commands_registry.add("seek")
    def seek_video(self, offset: int):
        if not self.__stream_layer.update_offset(offset):
            self.__tcp_channel.write_data("invalid seek position")
        self.__tcp_channel.write_data("ok")

    @commands_registry.add("stop")
    def stop(self):
        self.__stream_layer.stop()
        self.__tcp_channel.write_data("ok")
        raise StopSession()

    @commands_registry.add("pause")
    def pause(self):
        self.__stream_layer.pause()

    def wait_comands(self):
        while True:
            try:
                command_name, *args = self.__tcp_channel.read_datas()
                command_func = commands_registry.get_command(command_name)
                if not command_func:
                    self.__tcp_channel.write_data(f"command {command_name} doesn't found")
                    continue
                command_func(*args)
            except StopSession:
                return
