from .base_api import BaseAPI


class StreamAPI(BaseAPI):

    def request_a_video_package(self):
        self._tcp_channel.write_command("get_video_frame")

    def send_feedback(self, received_packages: int):
        self._tcp_channel.write_command("feedback", received_packages)
