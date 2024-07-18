import logging
import os
import socket
import struct
from threading import Thread

from server_schemes import command_schemes, response_schemas


CHUNK_SIZE = 4096
MTU = 1500-20-8 #1500 bytes (MTU size) - 20 bytes (IP header) - 8 bytes (UDP header)
MTU_VIDEO_BYTE_SIZE = MTU-4-4 # MTU - 4 bytes (integer offset size) - 4 bytes (integer data length)
EOFSYMBOL = struct.pack(f"ii{MTU_VIDEO_BYTE_SIZE}s", -1, 0, b"")

def serialize_data(offset: int, video_bytes: bytes):
    struct_format = f"ii{MTU_VIDEO_BYTE_SIZE}s"
    return struct.pack(struct_format, offset, len(video_bytes), video_bytes)

def send_packages(
    data: bytes,
    size_already_read:int,
    size_already_sended: int,
    client_connection_data: command_schemes.StartConnectionSchema,
    frame_request: command_schemes.FrameRequestSchema,
    udp_connection: socket.socket,
    client_address: str
):
    for i in range(0, len(data), MTU_VIDEO_BYTE_SIZE):
        serialized_datas = serialize_data(frame_request.offset+size_already_read+i, data[i:i+MTU_VIDEO_BYTE_SIZE])
        udp_connection.sendto(
            serialized_datas,
            (client_address, client_connection_data.udp_client_port)
        )
    return size_already_sended
def process_request(
    client_connection_data:command_schemes.StartConnectionSchema,
    frame_request: command_schemes.FrameRequestSchema,
    udp_connection: socket.socket,
    client_address:str
):
    logging.info("initiating the process of sending video packages...")
    with open(client_connection_data.path_video, 'rb') as video_file:
        video_file.seek(frame_request.offset)
        size_already_read = 0
        size_already_sended = 0
        for bytes_to_send in frame_request.reader_iterator():
            data = video_file.read(bytes_to_send)
            size_already_sended = send_packages(
                data, size_already_read, size_already_sended, client_connection_data,
                frame_request, udp_connection, client_address
            )
            if size_already_sended == -1:
                return
            size_already_read += bytes_to_send
    udp_connection.sendto(
        EOFSYMBOL,
        (client_address, client_connection_data.udp_client_port)
    )
    logging.info("video packages sent successfully")

def handle_client_connection(
    connection:socket.socket,
    address:tuple,
    client_connection_data:command_schemes.StartConnectionSchema
):
    video_size = os.path.getsize(client_connection_data.path_video)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        command = command_schemes.FrameRequestSchema.from_tcp_connection(connection)
        if video_size < command.offset + command.length:
            response = response_schemas.Response(
                status=response_schemas.ResponseStatusEnum.BAD_REQUEST,
                message='Invalid request, offset + length is greater than the video size'
            )
            response.send_to_tcp_connection(connection)
            logging.debug("ignoring an invalid request: %s", command.model_dump_json())
            continue
        response = response_schemas.Response(
            status=response_schemas.ResponseStatusEnum.OK,
            message=f'Will be send {command.length} bytes from offset {command.offset}'
        )
        response.send_to_tcp_connection(connection)
        process_request(
            client_connection_data=client_connection_data,
            frame_request=command,
            udp_connection=udp_socket,
            client_address=address[0]
        )

def starts_a_new_connection(
    connection:socket.socket,
    address:tuple
):
    logging.info("starts a new connection with %s", address[0])
    starts_handshake = command_schemes.StartConnectionSchema.from_tcp_connection(connection)
    if not os.path.exists(starts_handshake.path_video):
        response = response_schemas.VideoMetadasResponse(
            status=response_schemas.ResponseStatusEnum.BAD_REQUEST,
            message='Video not found',
            size=0,
            bitrate=0
        )
        response.send_to_tcp_connection(connection)
        logging.info("closing the connection because the requested video doesn't exist.")
        return
    response = response_schemas.VideoMetadasResponse.from_path_video(starts_handshake.path_video)
    worker_thread = Thread(
        target=handle_client_connection,
        args=(connection, address, starts_handshake)
    )
    response.send_to_tcp_connection(connection)
    worker_thread.start()
