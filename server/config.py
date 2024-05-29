from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    room_id_length: int = 6