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
        
        # Log request details
        try:
            request_body = await request.body()
            body_str = request_body.decode() if request_body else ""
            request_log = (
                f"\nRequest Details:\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Client IP: {request.client.host}\n"
                f"Method: {request.method}\n"
                f"Path: {request.url.path}\n"
                f"Headers: {dict(request.headers)}\n"
                f"Query Params: {dict(request.query_params)}\n"
                # f"Body: {body_str[:500] if len(body_str) > 500 else body_str}\n"
            )
            logging.info(request_log)
            
            # Process request and catch any errors
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response details
            response_log = (
                f"\nResponse Details:\n"
                f"Status: {response.status_code}\n"
                f"Duration: {process_time:.4f}s\n"
                f"Headers: {dict(response.headers)}\n"
            )
            logging.info(response_log)
            
        except Exception as e:
            # Log any unhandled exceptions
            error_log = (
                f"\nError Details:\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Error Type: {type(e).__name__}\n"
                f"Error Message: {str(e)}\n"
            )
            logging.error(error_log)
            raise
            
        finally:
            # Ensure logs are written
            logging.getLogger().handlers[0].flush()
            
        return response
