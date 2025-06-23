from src.grpc.gen import message_pb2
from src.grpc.gen import message_pb2_grpc
from src.grpc.gen import clipboard_pb2
from src.models.connection import Connection
from src.grpc.gen import auth_pb2
from google.protobuf import empty_pb2
import time
import asyncio
import grpc
from grpc_interceptor.exceptions import GrpcException
from loguru import logger

class MessageServicer(message_pb2_grpc.MessageServiceServicer):
    
    def __init__(self, connections: list[Connection]) -> None:
        super().__init__()
        self.connections = connections

    async def StreamMessages(self, request: auth_pb2.AuthRequest, context):
        print("StreamMessages Request Made with token: ", request.token)

        if request.token is None or request.token == "":
            raise GrpcException("Unauthorized")
        
        client_queue = asyncio.Queue()
        client_connection = context.peer()

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

    async def SendMessage(self, request: message_pb2.Message, context):

        logger.info(f"Received message: {request}")

        for connection in self.connections:
            if (connection.id != request.senderId):
                print("Sending message to connection: ", connection.id)
                await connection.queue.put(request)

        return empty_pb2.Empty()