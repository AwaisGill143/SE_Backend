"""
Custom middleware
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging
import json
import time

logger = logging.getLogger(__name__)

async def error_handling_middleware(request: Request, call_next):
    """
    Global error handling middleware
    """
    try:
        start_time = time.time()
        response = await call_next(request)
        
        # Log request details
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )
        
        return response
        
    except Exception as exc:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return Response(
            content=json.dumps({
                "detail": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.now().isoformat()
            }),
            status_code=500,
            media_type="application/json"
        )
