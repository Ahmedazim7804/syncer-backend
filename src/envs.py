import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_HOURS = float(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS"))
REFRESH_TOKEN_EXPIRE_HOURS = float(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS"))
ALGORITHM = os.getenv("ALGORITHM")