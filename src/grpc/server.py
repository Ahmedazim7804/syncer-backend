import grpc
from src.models.connection import Connection
from src.grpc.message_servicer import MessageServicer
from src.grpc.gen import syncer_pb2_grpc
from src.services.auth_service import AuthService
from src.core.container import Container
from dependency_injector.wiring import inject, Provide


@inject
class GrpcServer:
    connections: list[Connection] = []

    def __init__(
        self, port: int, auth_service: AuthService = Provide[Container.auth_service]
    ):
        self.port = port
        self.auth_service = auth_service

    def add_service(self):
        pass

    def stop(self):
        self.server.stop(0)

    async def run(self):
        self.server = grpc.aio.server()
        self.server.add_insecure_port(f"[::]:{self.port}")
        syncer_pb2_grpc.add_MessageServiceServicer_to_server(
            MessageServicer(self.connections, self.auth_service), self.server
        )
        await self.server.start()
        await self.server.wait_for_termination()

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def remove_connection(self, connection: Connection):
        self.connections.remove(connection)
