from fastapi import FastAPI
import logging

from api import router as api_router
from logging_config import setup_colored_logging, get_logger

setup_colored_logging(level=logging.INFO)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Assistant API",
    description="API for the personal assistant interpreter agent",
    version="1.0.0"
)

# Include the API router
app.include_router(api_router)

@app.get("/")
def root():
    """
    Root endpoint
    """
    return {
        "message": "Agent Interpreter API",
        "version": "v1",
        "available_endpoints": list_routes()
    }


def list_routes():
    """
    List all available routes in the FastAPI app.
    """
    route_list = []
    for route in api_router.routes:
        methods = list(route.methods)
        route_list.append({
            "path": route.path,
            "methods": methods,
            "name": getattr(route, 'name', 'unknown')
        })
    return route_list


def print_routes():
    """
    Print all available routes in the FastAPI app.
    """
    for route in api_router.routes:
        methods = ','.join(route.methods)
        logger.info(f"- {methods} {route.path}")