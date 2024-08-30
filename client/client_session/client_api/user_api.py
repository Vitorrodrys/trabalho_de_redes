from .base_api import BaseAPI


class UserAPI(BaseAPI):
    def seek(self, offset: int):
        self._tcp_channel.write_command("seek", offset)
        if self._tcp_channel.read_datas() == "invalid seek position":
            raise ValueError("invalid seek position")

    def seek_forward(self):
        self._tcp_channel.write_command("seek_forward")
        if self._tcp_channel.read_datas() == "invalid seek position":
            raise ValueError("invalid seek position")

    def seek_backward(self):
        self._tcp_channel.write_command("seek_backward")
        if self._tcp_channel.read_datas() == "invalid seek position":
            raise ValueError("invalid seek position")

    def stop(self):
        self._tcp_channel.write_command("stop")
        assert self._tcp_channel.read_datas() == "ok"
        self._tcp_channel.close()

    def pause(self):
        self._tcp_channel.write_command("pause")
