from data_channels import TCPChannel, UDPChannel

from .client_api import StreamAPI, UserAPI
from .stream_layer import StreamLayer

def starts_a_new_session(wished_video: str)->tuple[UserAPI, StreamLayer, int]:
    udp_channel = UDPChannel()
    tcp_channel, video_size = TCPChannel.create_tcp_channel(
        wished_video,
        udp_channel.get_listening_udp_port()
    )

    user_api = UserAPI(tcp_channel=tcp_channel)
    stream_api = StreamAPI(tcp_channel=tcp_channel)
    stream_layer = StreamLayer(stream_api, udp_channel=udp_channel)
    return user_api, stream_layer, video_size
