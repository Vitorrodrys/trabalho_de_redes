from enum import StrEnum
import os

from pydantic_settings import BaseSettings

class LogLevelsEnum(StrEnum):
    critical = "CRITICAL"
    fatal = "FATAL"
    error = "ERROR"
    warn = "WARN"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"

class ServerSettings(BaseSettings):
    # Server settings
    server_ip: str = os.getenv('SERVER_IP')
    server_port: int = os.getenv('SERVER_PORT')
    max_connections: int = os.getenv('MAX_CONNECTIONS')
    log_level: LogLevelsEnum = os.getenv('LOG_LEVEL', default="INFO")

class SessionSettings(BaseSettings):
    # Session settings
    window_size_increment: int = os.getenv("WINDOW_SIZE_INCREMENT")
    max_requests: int = os.getenv('MAX_REQUESTS')
    network_mtu: int = os.getenv('NETWORK_MTU')
    superior_threshould: int = os.getenv("SUPERIOR_THRESHOULD", default=str(2**17))

server_settings = ServerSettings()
session_settings = SessionSettings()
