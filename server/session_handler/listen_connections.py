import logging
import os
from threading import Thread

from core import server_settings

from .api_session import APISession, StreamLayer
from .data_channels import TCPChannel, UDPChannel


def starts_session(tcp_channel: TCPChannel, udp_channel: UDPChannel, video_path: str):
    stream_layer = StreamLayer(udp_channel, video_path)
    api_session = APISession(video_path, tcp_channel, stream_layer)
    tcp_channel.write_data(str(os.path.getsize(video_path)))
    api_session.wait_comands()
    return


def create_session(tcp_channel: TCPChannel, client_address: str):
    response = tcp_channel.read_datas()
    udp_port, video_path = response[0]
    logging.info(
        "starting a session with %s, streaming video %s to udp port %s",
        client_address,
        video_path,
        udp_port,
    )
    assert len(response[1:]) == 0
    if not os.path.exists(video_path):
        tcp_channel.write_data("error NotFound")
        return
    udp_channel = UDPChannel(client_address, int(udp_port))
    starts_session(tcp_channel, udp_channel, video_path)
    logging.info("Session with client %s was closed", client_address)


def listen_connections():
    tcp_socket = TCPChannel.create_tcp_socket(
        server_settings.server_ip, server_settings.server_port
    )
    logging.debug(
        "Server listening on %s:%d",
        server_settings.server_ip,
        server_settings.server_port,
    )
    while True:
        client_socket, client_address = tcp_socket.accept()
        logging.debug("Connection from %s:%d", *client_address)
        tcp_channel = TCPChannel(client_socket)
        Thread(target=create_session, args=(tcp_channel, client_address[0])).start()
