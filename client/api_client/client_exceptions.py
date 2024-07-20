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

class InvalidSeekPosition(ClientException):
    """
    Raised when the position to seek is invalid.
    """
    def __init__(self, position:int) -> None:
        super().__init__(f"the position {position} is invalid")