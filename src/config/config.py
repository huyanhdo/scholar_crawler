from pydantic import BaseSettings


class Settings(BaseSettings):
    nubela_key: str = "JS-CEFPeLRR8ackt8kY7vw"
    country: str = "australia"
    country_code: str = "704"
    database_linkedin: str = "linkedin"
    database_clutch: str = "clutch"
    database_wipo: str = "wipo"
    mongodb_username: str = "root"
    mongodb_password: str = "98859B9980A218F6DAD192B74781E15D"
    mongodb_host: str = "51.15.102.206"
    mongodb_port: int = 27017

settings = Settings()
