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
    max_wait_buffer_size: int = os.getenv('MAX_WAIT_BUFFER_SIZE', default="10")

class NetworkSettings(BaseSettings):
    mtu: int = os.getenv('MTU', default="1500")

    @computed_field
    @property
    def mtu_video_byte_size(self):
        return self.mtu - 4 - 4

server_settings = ServerSettings()
environment_settings = EnvironmentSettings()
network_settings = NetworkSettings()
