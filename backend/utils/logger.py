import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/api.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    encoding="utf-8",
    force=True
)

class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_body = await request.body()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        log_message = (
            f"Client: {request.client.host} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {process_time:.4f}s"
        )
        
        logging.info(log_message)
        logging.getLogger().handlers[0].flush()
        return response
