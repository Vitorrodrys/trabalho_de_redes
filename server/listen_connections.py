import socket

from core import environment_settings
from client_session import starts_a_new_connection


def listen_new_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((environment_settings.server_ip, environment_settings.server_port))
        server_sock.listen(environment_settings.max_connections)

        while True:
            client_sock, addr = server_sock.accept()
            starts_a_new_connection(client_sock, addr)
