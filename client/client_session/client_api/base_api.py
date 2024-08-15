from data_channels import TCPChannel


class BaseAPI:
    def __init__(self, tcp_channel: TCPChannel) -> None:
        self._tcp_channel = tcp_channel
