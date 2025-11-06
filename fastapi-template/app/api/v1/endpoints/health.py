"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Used for monitoring and load balancer health checks.

    Returns:
        Status message indicating the service is healthy
    """
    return {"status": "healthy"}
