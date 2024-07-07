import os

from pydantic_settings import BaseSettings


class EnvironmentSettings(BaseSettings):
    # Server settings
    server_ip: str = os.getenv('SERVER_IP')
    server_port: int = os.getenv('SERVER_PORT')
    max_connections: int = os.getenv('MAX_CONNECTIONS')


environment_settings = EnvironmentSettings()