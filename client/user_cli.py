

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

def interactive_seek(user_api: UserAPI, video_size: int):
    percentage_video = float(input("percentage video to seek: "))
    offset = int(video_size * percentage_video)
    user_api.seek(offset)

def interactive_cli():
    user_api, stream_layer, video_size = starts_user_session()

    commands = {
        "pause": user_api.pause,
        "seek":  lambda: interactive_seek(user_api, video_size),
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
