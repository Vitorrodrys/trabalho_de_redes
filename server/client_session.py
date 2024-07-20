import logging
import socket
from threading import Thread

import server_schemes
from stream_layer import StreamLayer, InvalidSeekPositionError

def handle_client_connection(
    connection:socket.socket,
    stream_layer: StreamLayer
):
    while True:
        command = server_schemes.SomeCommand.from_tcp_connection(connection)
        try:
            command.command.execute(stream_layer)
            response = server_schemes.Response(
                status= server_schemes.ResponseStatusEnum.OK
            )
            response.send_to_tcp_connection(connection)
        except server_schemes.StopConnection:
            connection.close()
            break
        except InvalidSeekPositionError as e:
            response = server_schemes.Response(
                status= server_schemes.ResponseStatusEnum.BAD_REQUEST,
                message=f"Invalid seek position {e.seek_position}"
            )
            response.send_to_tcp_connection(connection)
def starts_a_new_connection(
    connection:socket.socket,
    address:tuple
):
    logging.info("starts a new connection with %s", address[0])
    client_session = server_schemes.SessionConnectionSchema.from_tcp_connection(connection)
    stream_layer = StreamLayer(
        path_video=client_session.path_video,
        udp_port=client_session.udp_port,
        client_address=address[0]
    )    
    response = server_schemes.VideoMetadasResponse.from_path_video(client_session.path_video)
    worker_thread = Thread(
        target=handle_client_connection,
        args=(connection, stream_layer)
    )
    response.send_to_tcp_connection(connection)
    worker_thread.start()
