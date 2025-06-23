import grpc
from concurrent import futures
from src.models.connection import Connection
from src.environment import Environment
import asyncio
from src.grpc.message_servicer import MessageServicer
from src.grpc.gen import message_pb2_grpc
from src.grpc.interceptors import AuthInterceptor

class GrpcServer:
    connections: list[Connection] = []
    def __init__(self, port: int):
        self.port = port

    def add_service(self):
        pass

    def stop(self):
        self.server.stop(0)

    async def run(self):
        self.server = grpc.aio.server(interceptors=[AuthInterceptor()])
        self.server.add_insecure_port(f"[::]:{self.port}")
        message_pb2_grpc.add_MessageServiceServicer_to_server(MessageServicer(self.connections), self.server)
        await self.server.start()
        await self.server.wait_for_termination()

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def remove_connection(self, connection: Connection):
        self.connections.remove(connection)