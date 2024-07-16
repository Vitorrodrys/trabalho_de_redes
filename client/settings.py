import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_address: str = os.getenv('SERVER_ADDRESS')
    server_port: int = os.getenv('SERVER_PORT')

environment_settings = Settings()
