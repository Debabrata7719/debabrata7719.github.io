"""
routes/health.py — Health check endpoint.

Accepts both GET and HEAD requests so that load balancers, uptime
monitors, and deployment platforms can probe the service with minimal
overhead.

Response (GET):
    {"status": "running", "processed": true}

Response (HEAD):
    HTTP 200 with no body (headers only).
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Health"])


@router.api_route(
    "/health",
    methods=["GET", "HEAD"],
    summary="Health check",
    description=(
        "Returns service status. "
        "GET returns a JSON body; HEAD returns HTTP 200 with no body."
    ),
)
async def health_check():
    """Lightweight probe used by uptime monitors and deployment platforms."""
    return JSONResponse(
        status_code=200,
        content={"status": "running", "processed": True},
    )
