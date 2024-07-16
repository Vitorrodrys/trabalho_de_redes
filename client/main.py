from controller import Controller
from api_client.client_exceptions import VideoNotFoundException

def user_handler():
    video_name = input("Enter the video name: ")
    try:
        controller = Controller(wished_video=video_name)
    except VideoNotFoundException:
        print(f"The requested video \"{video_name}\" was not found in server")
        return

    while True:
        user_command = input("type a command")
        if user_command == "pause":
            controller.pause()
        elif user_command == "seek":
            percentage = float(input("Enter the percentage: "))
            controller.seek_video(percentage)
def main():
    user_handler()

if __name__ == '__main__':
    main()
