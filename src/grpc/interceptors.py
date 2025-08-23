import grpc
from src.services.auth_service import AuthService


class AuthInterceptor(grpc.aio.ServerInterceptor):
    def __init__(self, auth_service: AuthService = AuthService):
        self.auth_service = auth_service

    async def intercept_unary_unary(self, request, context, handler):
        if not self.verify_token(request, isIterator=False):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")
        return await handler.unary_unary(request, context)

    async def intercept_server_stream(self, request, context, handler):
        if not self.verify_token(request, isIterator=False):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")
            return

        async for response in handler.unary_stream(request, context):
            yield response

    async def intercept_client_stream(self, request_iterator, context, handler):
        if not self.verify_token(request_iterator, isIterator=True):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")
        return await handler.stream_unary(request_iterator, context)

    async def intercept_bi_di_stream(self, request_iterator, context, handler):
        if not self.verify_token(request_iterator, isIterator=True):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")

        async def _iter():
            async for response in handler.stream_stream(request_iterator, context):
                yield response

        return _iter()

    def verify_token(self, request, isIterator: bool = False) -> bool:
        token = None
        try:
            token = request.token
        except Exception:
            return False

        return self.auth_service.verifyAccessToken(token) is not None

    async def intercept_service(self, continuation, handler_call_details):
        _ = handler_call_details.method.split("/")[-1]

        handler = await continuation(handler_call_details)
        if handler is None:
            return None

        if handler.unary_unary:

            async def _unary_unary(request, context):
                return await self.intercept_unary_unary(request, context, handler)

            return grpc.unary_unary_rpc_method_handler(
                _unary_unary,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.unary_stream:

            async def _unary_stream(request, context):
                async for response in self.intercept_server_stream(
                    request, context, handler
                ):
                    yield response

            return grpc.unary_stream_rpc_method_handler(
                _unary_stream,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_unary:

            async def _stream_unary(request_iterator, context):
                return await self.intercept_client_stream(
                    request_iterator, context, handler
                )

            return grpc.stream_unary_rpc_method_handler(
                _stream_unary,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_stream:

            async def _stream_stream(request_iterator, context):
                return await self.intercept_bi_di_stream(
                    request_iterator, context, handler
                )

            return grpc.stream_stream_rpc_method_handler(
                _stream_stream,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        return handler
