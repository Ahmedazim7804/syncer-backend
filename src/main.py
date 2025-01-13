from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from src.api.v1.routes import routers as api_v1_routers
from src.core.middleware import VerifyTokenMiddleware
from src.core.container import Container
from fastapi.routing import APIRoute

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:1420"
]

container = Container()
container.db()


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