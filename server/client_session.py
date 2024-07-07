import os
import socket

from server_schemes import command_schemes, response_schemas

def process_request(
    video_path: str,
    size_requested: int,
    offset: int,
    udp_connection: socket.socket,
    client_address:tuple[str, int]
):
    with open(video_path, 'rb') as video_file:
        video_file.seek(offset)
        size_already_read = 0
        while size_already_read < size_requested:
            bytes_to_send = min(4096, size_requested - size_already_read)
            data = video_file.read(bytes_to_send)
            udp_connection.sendto(data, client_address)
            size_already_read += len(data)

def handle_client_connection(
    connection:socket.socket,
    address:tuple,
    path_to_video:str,
    udp_client_port:int
):
    video_size = os.path.getsize(path_to_video)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        command = connection.recv(1024).decode('utf-8')
        command = command_schemes.VideoBytesRequestSchema.model_validate_json(command)
        if video_size < command.offset + command.length:
            response = response_schemas.Response(
                status=response_schemas.ResponseStatusEnum.BAD_REQUEST,
                message='Invalid request, offset + length is greater than the video size'
            )
            connection.send(response.model_dump_json().encode('utf-8'))
            continue
        process_request(
            video_path=path_to_video,
            size_requested=command.length,
            offset=command.offset,
            udp_connection=udp_socket,
            client_address=(address[0], udp_client_port)
        )
        response = response_schemas.Response(
            status=response_schemas.ResponseStatusEnum.OK,
            message=f'Request completed, was sent {command.length} bytes from offset {command.offset}'
        )
        connection.send(response.model_dump_json().encode('utf-8'))
    
    