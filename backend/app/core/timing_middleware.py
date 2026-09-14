"""FastAPI timing middleware.

Adds an X-Response-Time-Ms header to every response and logs structured
timing data for chat and search endpoints.
"""

import logging
import time

from fastapi import Request

logger = logging.getLogger(__name__)


async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"

    path = request.url.path
    if path.startswith("/api/v1/chat") or path.startswith("/api/v1/search"):
        logger.info(
            "timing",
            extra={
                "path": path,
                "duration_ms": round(elapsed_ms, 2),
                "status_code": response.status_code,
            },
        )

    return response
