import grpc
from src.core.config import Config
from src.models.connection import Connection
from src.grpc.message_servicer import MessageServicer
from src.grpc.gen import syncer_pb2_grpc
from src.services.auth_service import AuthService
from src.core.container import Container
from dependency_injector.wiring import inject, Provide
import os


@inject
class GrpcServer:
    connections: list[Connection] = []

    def __init__(
        self, port: int, auth_service: AuthService = Provide[Container.auth_service]
    ):
        self.port = port
        self.auth_service = auth_service
        self.server_cert, self.server_key, self.ca_cert = self.load_cert()

    def add_service(self):
        pass

    def stop(self):
        self.server.stop(0)

    async def run(self):
        server_creds = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[(self.server_key, self.server_cert)],
            root_certificates=self.ca_cert,
            require_client_auth=True,
        )

        self.server = grpc.aio.server()
        self.server.add_secure_port(f"[::]:{self.port}", server_creds)

        syncer_pb2_grpc.add_MessageServiceServicer_to_server(
            MessageServicer(self.connections, self.auth_service), self.server
        )
        await self.server.start()
        await self.server.wait_for_termination()

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def remove_connection(self, connection: Connection):
        self.connections.remove(connection)

    def load_cert(self) -> tuple[bytes, bytes]:
        base_path = Config.CERTS_PATH
        try:
            with open(os.path.join(base_path, "server.crt"), "rb") as f:
                server_cert = f.read()
            with open(os.path.join(base_path, "server.key"), "rb") as f:
                server_key = f.read()
            with open(os.path.join(base_path, "ca.crt"), "rb") as f:
                ca_cert = f.read()

            return (server_cert, server_key, ca_cert)
        except Exception as e:
            raise Exception(f"Failed to load cert: {e}")
