import sys
import os

gen_path = os.path.join(os.path.dirname(__file__), "grpc", "gen")
if gen_path not in sys.path:
    sys.path.insert(0, gen_path)

from fastapi import FastAPI  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402
from src.api.v1.routes import routers as api_v1_routers  # noqa: E402
from src.core.middleware import VerifyTokenMiddleware  # noqa: E402
from src.core.container import Container  # noqa: E402
from src.grpc.server import GrpcServer  # noqa: E402
import asyncio  # noqa: E402
import uvicorn  # noqa: E402


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:1420",
]


app = FastAPI()

app.add_middleware(VerifyTokenMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_routers)


async def main():
    container = Container()
    container.db()
    container.wire(modules=[__name__])

    fastApiConfig = uvicorn.Config(app, host="0.0.0.0", port=8000)
    fastApiServer = uvicorn.Server(config=fastApiConfig)

    grpcServer = GrpcServer("50051")

    await asyncio.gather(fastApiServer.serve(), grpcServer.run())


if __name__ == "__main__":
    asyncio.run(main())
