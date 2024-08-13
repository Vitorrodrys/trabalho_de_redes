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
    cluster_size: int = os.getenv('CLUSTER_SIZE', default=str(4096))
    max_requests: int = os.getenv('MAX_REQUESTS')
    network_mtu: int = os.getenv('NETWORK_MTU')
    upper_threshould: int = os.getenv("UPPER_THRESHOULD", default=str(2**18))

server_settings = ServerSettings()
session_settings = SessionSettings()
