import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_HOURS = float(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS"))
    REFRESH_TOKEN_EXPIRE_HOURS = float(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS"))
    ALGORITHM = os.getenv("ALGORITHM")
    PASSWORD = os.getenv("PASSWORD")
    DB_URL = (
        os.getenv("DB_URL")
        if (os.getenv("DB_URL") is not None)
        else "sqlite:///database.db"
    )
    CERTS_PATH = os.getenv("CERTS_PATH")
