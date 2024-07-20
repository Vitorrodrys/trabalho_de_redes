from enum import Enum
import os

from pydantic import computed_field
from pydantic_settings import BaseSettings

class LogLevelsEnum(str, Enum):
    critical = "CRITICAL"
    fatal = "FATAL"
    error = "ERROR"
    warn = "WARN"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"

class ServerSettings(BaseSettings):
    server_address: str = os.getenv('SERVER_ADDRESS')
    server_port: int = os.getenv('SERVER_PORT')
    
class EnvironmentSettings(BaseSettings):
    log_level: LogLevelsEnum = os.getenv('LOG_LEVEL', default="ERROR")
    mpv_frames_size: int = os.getenv('MPV_FRAMES_SIZE', default="100")

class NetworkSettings(BaseSettings):
    mtu: int = os.getenv('MTU', default="1472")

    @computed_field
    @property
    def mtu_video_byte_size(self)->int:
        return self.mtu - 4 - 4

server_settings = ServerSettings()
environment_settings = EnvironmentSettings()
network_settings = NetworkSettings()
