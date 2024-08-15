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


class EnvironmentSettings(BaseSettings):
    log_level: str = os.getenv("LOG_LEVEL", default="INFO")
    server_ip: str = os.getenv("SERVER_IP")
    server_port: int = os.getenv("SERVER_PORT")


class SessionSettings(BaseSettings):
    udp_channel_timeout: float = os.getenv("UDP_CHANNEL_TIMEOUT", default="2")
    network_mtu: int = os.getenv("NETWORK_MTU", default="1500")


session_settings = SessionSettings()
enviroment_settings = EnvironmentSettings()
