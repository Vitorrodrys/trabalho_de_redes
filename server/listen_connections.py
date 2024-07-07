import logging
import os
import socket
from threading import Thread

from settings import environment_settings
from server_schemes import hand_shake_schemas, response_schemas
from client_session import handle_client_connection

def starts_a_new_connection(
    connection:socket.socket,
    address:tuple
):
    logging.info("starts a new connection with %s", address[0])
    starts_handshake = connection.recv(1024).decode('utf-8')
    starts_handshake = hand_shake_schemas.StartConnectionSchema.model_validate_json(
        starts_handshake
    )
    if not os.path.exists(starts_handshake.path_video):
        response = response_schemas.VideoMetadasResponse(
            status=response_schemas.ResponseStatusEnum.BAD_REQUEST,
            message='Video not found',
            size_video=0
        )
        connection.send(response.model_dump_json().encode('utf-8'))
        connection.close()
        logging.info("closing the connection because the requested video doesn't exist.")
        return
    response = response_schemas.VideoMetadasResponse(
        status=response_schemas.ResponseStatusEnum.OK,
        message="Video metadatas",
        size_video=os.path.getsize(starts_handshake.path_video)
    )
    worker_thread = Thread(
        target=handle_client_connection,
        args=(connection, address, starts_handshake.path_video, starts_handshake.udp_client_port)
    )
    connection.send(response.model_dump_json().encode('utf-8'))
    worker_thread.start()

def listen_new_connections():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((environment_settings.server_ip, environment_settings.server_port))
    server_sock.listen(environment_settings.max_connections)

    while True:
        client_sock, addr = server_sock.accept()
        starts_a_new_connection(client_sock, addr)
