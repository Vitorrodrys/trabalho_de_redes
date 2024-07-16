class ClientException(Exception):
    """
    A generic exception for the client package.
    """

class VideoNotFoundException(ClientException):
    """
    Raised when the video requested doesn't exist in the server.
    """
    def __init__(self, video_name:str) -> None:
        super().__init__(f"the video {video_name} was not found in the server")
