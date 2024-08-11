import logging
import os
from threading import Thread

from core import server_settings

from .data_channels import TCPChannel, UDPChannel
from .api_session import starts_session

def create_session(tcp_channel: TCPChannel, client_address:str):
    udp_port, video_path = tcp_channel.read_datas()
    if not os.path.exists(video_path):
        tcp_channel.write_data("error NotFound")
        return
    udp_channel = UDPChannel(client_address, udp_port)
    tcp_channel.write_data(os.path.getsize(video_path))
    starts_session(tcp_channel, udp_channel, video_path)

def listen_connections():

    tcp_socket = TCPChannel.create_tcp_socket(server_settings.server_ip, server_settings.server_port)
    logging.debug("Server listening on %s:%d", server_settings.server_ip, server_settings.server_port)
    while True:
        client_socket, client_address = tcp_socket.accept()
        logging.debug("Connection from %s:%d", *client_address)
        tcp_channel = TCPChannel(client_socket)
        Thread(target=create_session, args=(tcp_channel, client_address)).start()
