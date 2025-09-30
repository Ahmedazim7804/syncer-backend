import grpc
from src.services.auth_service import AuthService
from src.core.metadata import PUBLIC_ROUTES


class AuthInterceptor(grpc.aio.ServerInterceptor):
    def __init__(self, auth_service: AuthService = AuthService):
        self.auth_service = auth_service

    def verify_token_from_metadata(self, context) -> bool:
        """Extract and verify token from request metadata (headers)"""
        try:
            metadata = dict(context.invocation_metadata())
            # Support both 'authorization' and 'token' metadata keys
            token = metadata.get('authorization', '')
            if token.startswith('Bearer '):
                token = token[7:]  # Remove 'Bearer ' prefix
            elif not token:
                token = metadata.get('token', '')
            
            if not token:
                return False
            
            return self.auth_service.verifyAccessToken(token) is not None
        except Exception:
            return False

    async def intercept_unary_unary(self, request, context, handler):
        if not self.verify_token_from_metadata(context):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")
        return await handler.unary_unary(request, context)

    async def intercept_server_stream(self, request, context, handler):
        if not self.verify_token_from_metadata(context):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")
            return

        async for response in handler.unary_stream(request, context):
            yield response

    async def intercept_client_stream(self, request_iterator, context, handler):
        if not self.verify_token_from_metadata(context):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")
            return None
        
        return await handler.stream_unary(request_iterator, context)

    async def intercept_bi_di_stream(self, request_iterator, context, handler):
        if not self.verify_token_from_metadata(context):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")
            return

        async for response in handler.stream_stream(request_iterator, context):
            yield response

    async def intercept_service(self, continuation, handler_call_details):
        handler = await continuation(handler_call_details)

        if handler_call_details.method in PUBLIC_ROUTES:
            return handler

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
                # Fixed: properly yield from the async generator
                async for response in self.intercept_bi_di_stream(
                    request_iterator, context, handler
                ):
                    yield response

            return grpc.stream_stream_rpc_method_handler(
                _stream_stream,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        return handler