import asyncio
import time
import uuid
from google.protobuf import empty_pb2
from loguru import logger
from src.grpc.gen import syncer_pb2_grpc
from src.models.connection import Connection
from src.services.auth_service import AuthService
from src.grpc.gen.syncer_pb2 import (
    ClientMessage,
    ServerMessage,
    MessageType,
    AuthResponse,
    google_dot_protobuf_dot_wrappers__pb2,
)
from src.core.security import TokenData


class MessageServicer(syncer_pb2_grpc.MessageServiceServicer):
    def __init__(
        self, connections: list[Connection], auth_service: AuthService
    ) -> None:
        super().__init__()
        self.connections = connections
        self.auth_service = auth_service

    async def IsConnected(self, request: empty_pb2.Empty, context):
        return google_dot_protobuf_dot_wrappers__pb2.BoolValue(value=True)

    async def StreamMessages(self, request: ClientMessage, context):
        logger.info(f"StreamMessages Request Made with token: {request.token}")

        if request.token is None or request.token == "":
            logger.error("No token provided")
            yield self.construct_message(
                type=MessageType.AUTH,
                message=AuthResponse(message="Unauthorized"),
                senderId="server",
            )
            return

        if not self.auth_service.verifyAccessToken(request.token):
            logger.error("Invalid or Expired access token")
            yield self.construct_message(
                type=MessageType.AUTH,
                message=AuthResponse(message="Unauthorized"),
                senderId="server",
            )
            return

        client_queue = asyncio.Queue()

        connection = Connection(id=request.token, queue=client_queue)
        self.connections.append(connection)

        logger.info(f"New connection established: {connection.id}")

        try:
            while True:
                message = await client_queue.get()

                yield message
        except Exception as e:
            logger.error(f"Error in StreamMessages: {e}")
        finally:
            self.connections.remove(connection)
            logger.info(f"Connection closed: {connection.id}")

    async def SendMessage(self, request: ClientMessage, context):
        logger.info(f"Received message: {request}")

        tokenData: TokenData | None = self.auth_service.verifyAccessToken(request.token)

        if tokenData is None:
            logger.error("Invalid or Expired access token")
            return empty_pb2.Empty()

        messageType = request.type
        payload = self.extract_payload(request)

        for connection in self.connections:
            if connection.id != tokenData.id:
                print("Sending message to connection: ", connection.id)
                await connection.queue.put(
                    self.construct_message(
                        message=payload, type=messageType, senderId=tokenData.id
                    )
                )

        return empty_pb2.Empty()

    def construct_message(
        self, message: any, type: MessageType, senderId: str
    ) -> ServerMessage:
        message = ServerMessage(
            id=str(uuid.uuid4()),
            senderId=senderId,
            createdAt=int(time.time() * 1000),
            type=type,
            clipboard=message if type == MessageType.CLIPBOARD else None,
            auth=message if type == MessageType.AUTH else None,
            genericText=message if type == MessageType.GENERIC_TEXT else None,
        )

        return message

    def extract_payload(self, request: ClientMessage) -> any:
        match request.type:
            case MessageType.CLIPBOARD:
                return request.clipboard
            case MessageType.GENERIC_TEXT:
                return request.genericText
            case _:
                return None
