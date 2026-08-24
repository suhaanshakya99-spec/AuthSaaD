from pydantic_settings import (BaseSettings, SettingsConfigDict)

class Settings(BaseSettings):

    POSTGRESQL_URL:str
    ALGORITHM:str
    KEY:str
    ACESS_TOKEN_EXPIRE:int
    REFRESH_TOKEN_EXPIRE:int

    RESEND_API:str
    SENDER_EMAIL:str

    BROKER_URL:str
    BACKEND_URL:str


    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()