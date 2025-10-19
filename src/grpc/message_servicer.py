import asyncio
import time
import uuid
from google.protobuf import empty_pb2
from loguru import logger
from src.grpc.gen import syncer_pb2_grpc
from src.models.connection import Connection
from src.services.auth_service import AuthService
from datetime import datetime
from sqlalchemy import event
from sqlmodel import Session
from src.schema.auth_schema import User
from typing import Optional
from src.grpc.gen.syncer_pb2 import (
    ClientMessage,
    ServerMessage,
    MessageType,
    ConnectedDevices,
    DeviceInfo,
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

    async def IsReachable(self, request: empty_pb2.Empty, context):
        return google_dot_protobuf_dot_wrappers__pb2.BoolValue(value=True)

    def extractUserToken(self, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get("authorization", "")
        if token.startswith("Bearer "):
            token = token[7:]

        logger.info(f"StreamMessages Request Made with token: {token}")
        tokenData: TokenData | None = self.auth_service.verifyAccessToken(token)
        tokenData = self.auth_service.verifyAccessToken(token)

        return tokenData

    async def handleUserMessage(self, message: ClientMessage, context):
        if message.type == MessageType.SERVER_COMMAND:
            await self.handleServerCommand(
                message.ServerCommand.command, message.ServerCommand.data, context
            )
        elif message.type == MessageType.CLIPBOARD:
            pass
        elif message.type == MessageType.GENERIC_TEXT:
            pass
        elif message.type == MessageType.CONNECTED_DEVICES:
            pass
        else:
            logger.error(f"Unknown message type: {message.type}")

    async def handleServerCommand(self, command: str, data: dict, context):
        if command == "refresh":
            await self.broadcast(sender="sender", message=self.get_all_devices())
        else:
            pass

    async def StreamMessages(self, request: ClientMessage, context):
        tokenData = self.extractUserToken(context)
        connection_id = tokenData.id

        if connection_id in self.connections.keys():
            self.connections[connection_id].active = True
        else:
            self.connections[connection_id] = Connection(
                id=connection_id,
                active=True,
                client=self.auth_service.getUser(connection_id),
                queue=asyncio.Queue(),
            )

        await self.broadcast(sender="sender", message=self.get_all_devices())

        logger.info(f"New connection established: {connection_id}")

        try:
            while True:
                message = await self.connections[connection_id].queue.get()

                yield message
        except Exception as e:
            logger.error(f"Error in StreamMessages: {e}")
        finally:
            self.auth_service.updateUser(id=connection_id, last_seen=datetime.now())
            self.connections.pop(connection_id)
            await self.broadcast(sender="sender", message=self.get_all_devices())
            logger.info(f"Connection closed: {connection_id}")

    async def SendMessage(self, request_iterator, context):
        async for request in request_iterator:
            logger.info(f"Received message: {request}")

            tokenData = self.extractUserToken(context)
            messageType = request.type
            payload = self.extract_payload(request)

            asyncio.create_task(self.handleUserMessage(request, context))

            # await self.broadcast(
            #     tokenData.id,
            #     self.construct_message(
            #         message=payload, type=messageType, senderId=tokenData.id
            #     ),
            # )

        return empty_pb2.Empty()

    def construct_message(
        self, message: any, type: MessageType, senderId: str
    ) -> ServerMessage:
        message = ServerMessage(
            id=str(uuid.uuid4()),
            senderId=senderId,
            createdAt=int(time.time() * 1000),
            type=type,
            Clipboard=message if type == MessageType.CLIPBOARD else None,
            GenericText=message if type == MessageType.GENERIC_TEXT else None,
            ConnectedDevices=message if type == MessageType.CONNECTED_DEVICES else None,
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

    def get_all_devices(self):
        message = ServerMessage(
            id=str(uuid.uuid4()),
            senderId="sender",
            createdAt=int(time.time() * 1000),
            type=MessageType.CONNECTED_DEVICES,
            ConnectedDevices=ConnectedDevices(
                devices=[
                    DeviceInfo(
                        id=connection.client.id,
                        ip=connection.client.ip,
                        name=connection.client.device,
                        connected=True if connection.active is True else False,
                        last_seen=int(connection.client.last_seen.timestamp()),
                    )
                    for connection in self.connections.values()
                ]
            ),
        )

        return message

    async def broadcast(self, sender: str, message, to: Optional[list[str]] = None):
        recievers = (
            self.connections.values()
            if to is None
            else filter(
                lambda connection: connection.id in to, self.connections.values()
            )
        )

        if to is None:
            for connection in recievers:
                if connection.id != sender and connection.active:
                    print("Sending message to connection: ", connection.id)
                    await connection.queue.put(message)
