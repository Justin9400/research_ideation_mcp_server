from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

class MCPMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization")
        if auth != f"Bearer {self.api_key}":
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized: Invalid or missing API key"}
            )
        return await call_next(request)
