from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_host: str = "51.15.59.131"
    # mongodb_host: str = "compose_mongodb_1"
    mongodb_port: int = 27017
    mongodb_username: str = "root"
    mongodb_password: str = "98859B9980A218F6DAD192B74781E15D"
    # stocks_list_path: str = "/opt/airflow/src/data/selected_stocks.csv"
    # commodity_path: str = "/opt/airflow/src/data/selected_commodities.csv"
    # stocks_list_path: str = "./src/data/selected_stocks.csv"
    # tele_token: str = "1995986048:AAEXtScm9HtMqaasiVJO5rqlA7SVk4Q_iHM"
    # tele_chat_id: str = "-1001544897561"
    # aws_endpoint_url: str = "https://sgp1.digitaloceanspaces.com"
    # aws_access_key_id: str = "DO00DFFH7WPR3WHBW2ZY"
    # aws_secret_access_key: str = "B0LNUj/ENUfFvB6VuieoT35nWXw+EsHWJEC2gBBzndk"
    # bucket_name: str = "vnstocks-crawler"
    # fireant_bearer_token: str = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSIsImtpZCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4iLCJhdWQiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4vcmVzb3VyY2VzIiwiZXhwIjoxOTYwNjU3NTgwLCJuYmYiOjE2NjA2NTc1ODAsImNsaWVudF9pZCI6ImZpcmVhbnQudHJhZGVzdGF0aW9uIiwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsInJvbGVzIiwiZW1haWwiLCJhY2NvdW50cy1yZWFkIiwiYWNjb3VudHMtd3JpdGUiLCJvcmRlcnMtcmVhZCIsIm9yZGVycy13cml0ZSIsImNvbXBhbmllcy1yZWFkIiwiaW5kaXZpZHVhbHMtcmVhZCIsImZpbmFuY2UtcmVhZCIsInBvc3RzLXdyaXRlIiwicG9zdHMtcmVhZCIsInN5bWJvbHMtcmVhZCIsInVzZXItZGF0YS1yZWFkIiwidXNlci1kYXRhLXdyaXRlIiwidXNlcnMtcmVhZCIsInNlYXJjaCIsImFjYWRlbXktcmVhZCIsImFjYWRlbXktd3JpdGUiLCJibG9nLXJlYWQiLCJpbnZlc3RvcGVkaWEtcmVhZCJdLCJzdWIiOiI0ZTM0MDgxYi0xNzEyLTRhOGQtYTgxOC02NWJlYTg1MWJhY2YiLCJhdXRoX3RpbWUiOjE2NjA2NTc1ODAsImlkcCI6Imlkc3J2IiwibmFtZSI6InRoYW5odHJ1bmdodXluaDkzQGdtYWlsLmNvbSIsInNlY3VyaXR5X3N0YW1wIjoiYzJlNmI0ZGQtZDUwOS00Y2I0LWFmNTYtOGM3MjU0YWYwOTc1IiwianRpIjoiNWFiYmE3YzE4YjQ5NThmMDNiODA4MDUxZTI0N2ZlZWIiLCJhbXIiOlsicGFzc3dvcmQiXX0.D_qs5B3VpqDmBcVsm22maxUkBs5b3DJOeQsZ0FzzX0sYldne2TCudWcxyGMOizBjYwMTT-A2R6neea1Rrl5-PjSUMfql2JxyQDfDc1lYUb0ugDKBIwu_4K_MmAtmDTHMIy-9Fd0gmr_pb6ZuKs3W58tfJcy2AZOH6nBn5FvU2Zauem7Sqet6qMtd8Uvl7RBm7o6QqGI1mfgEnTaTKA84mMkSZBo09jFlb1LXDLA1A4UUEVRcZGfMZJx5eO27PaH3XSg0DSOepPN-fvHbmnhfCE6JMSQOAlIery6hGXuZawng3isD_rcotTjHIKsmIwwHBejoz3J_LGju_2Dz2w4nhA"

settings = Settings()
