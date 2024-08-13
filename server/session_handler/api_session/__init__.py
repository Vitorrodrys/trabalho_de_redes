from session_handler.data_channels import TCPChannel, UDPChannel

from .api_session import APISession
from .stream_layer import StreamLayer


def starts_session(
    tcp_channel: TCPChannel,
    udp_channel: UDPChannel,
    video_path: str
):
    stream_layer = StreamLayer(udp_channel, video_path)
    api_session = APISession(tcp_channel, stream_layer)
    api_session.wait_comands()
    return
    