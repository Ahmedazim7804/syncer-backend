from grpc_interceptor import ServerInterceptor
from grpc_interceptor.exceptions import GrpcException
from typing import Awaitable, Callable, Any, Coroutine
import grpc
from grpc import HandlerCallDetails, RpcMethodHandler
from grpc.aio import ServerInterceptor


class AuthInterceptor(ServerInterceptor):
    async def intercept_service(
        self,
        continuation: Callable[[HandlerCallDetails], Awaitable[RpcMethodHandler]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Coroutine[Any, Any, RpcMethodHandler]:
        return await continuation(handler_call_details)
