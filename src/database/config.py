from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_host: str = "51.15.59.131"
    mongodb_port: int = 27017
    mongodb_username: str = "root"
    mongodb_password: str = "98859B9980A218F6DAD192B74781E15D"

settings = Settings()
