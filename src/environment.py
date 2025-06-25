from dotenv import load_dotenv
import os

load_dotenv()


class Environment:
    GRPC_PORT: str = os.getenv("GRPC_PORT", "50051")
