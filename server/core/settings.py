from enum import Enum
import os

from pydantic_settings import BaseSettings

class LogLevelsEnum(str, Enum):
    critical = "CRITICAL"
    fatal = "FATAL"
    error = "ERROR"
    warn = "WARN"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"

class EnvironmentSettings(BaseSettings):
    # Server settings
    server_ip: str = os.getenv('SERVER_IP')
    server_port: int = os.getenv('SERVER_PORT')
    max_connections: int = os.getenv('MAX_CONNECTIONS')
    block_size_sended_per_iteration: int = os.getenv('BLOCK_SIZE_SENDED_PER_ITERATION')
    log_level: LogLevelsEnum = os.getenv('LOG_LEVEL', default="INFO")


environment_settings = EnvironmentSettings()