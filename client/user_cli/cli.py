from api_client import ApiClient, client_exceptions, schemes
from core import server_settings

from .user_commands import UserCommand, PauseCommand, SeekCommand, StopCommand

def interpreter_commands(api_client: ApiClient, video_metadatas:schemes.VideoMetadasResponse):
    parameters = {
        "api_client": api_client,
        "video_metadatas":video_metadatas
    }
    commands: dict[str, UserCommand] = {
        "pause": PauseCommand(**parameters),
        "stop": StopCommand(**parameters),
        "seek": SeekCommand(**parameters)
    }
    user_input = input("Type a command: ")
    while user_input != 'stop':
        command = commands.get(user_input, None)
        if not command:
            print("invalid command, avaible commands are: pause, stop or seek")
            continue
        command.execute()
    print("leaving...")
def interactive_cli():
    video_name = input("Enter the video name: ")
    try:
        api_client, video_metadatas = ApiClient.create_session(
            server_settings.server_address,
            server_settings.server_port,
            video_name
        )
    except client_exceptions.VideoNotFoundException:
        print(f"The video {video_name} was not found")
        return

    interpreter_commands(
        api_client=api_client,
        video_metadatas=video_metadatas
    )
