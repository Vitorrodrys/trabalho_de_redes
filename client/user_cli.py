

from client_session import starts_a_new_session, StreamLayer, UserAPI

def starts_user_session()->tuple[UserAPI, StreamLayer, int]:
    while True:
        video_path = input("video path: ")
        try:
            user_api, stream_layer, video_size = starts_a_new_session(video_path)
        except ValueError:
            print("video not found in server")
            continue
        break
    return user_api, stream_layer, video_size

def interactive_seek(user_api: UserAPI, stream_layer:StreamLayer, video_size: int):
    percentage_video = float(input("percentage video to seek: "))/100
    offset = int(video_size * percentage_video)
    with stream_layer.get_lock():
        user_api.seek(offset)
def interactive_pause(user_api: UserAPI, stream_layer: StreamLayer):
    stream_layer.pause()
    user_api.pause()

def _interactive_cli(user_api: UserAPI, stream_layer: StreamLayer, video_size: int):
    commands = {
        "pause": lambda: interactive_pause(user_api, stream_layer),
        "seek":  lambda: interactive_seek(user_api, stream_layer, video_size),
        "quit":  user_api.stop
    }
    command = input("type a command: ")
    while command != "quit":
        if command in commands:
            commands[command]()
        command = input("type a command: ")
    user_api.stop()
    stream_layer.stop()
    print("session closed")

def interactive_cli():
    user_api, stream_layer, video_size = starts_user_session()
    try:
        _interactive_cli(user_api, stream_layer, video_size)
    finally:
        user_api.stop()
        stream_layer.stop()
        print("session closed")
