"""Application factory for Quart application.

This module implements the application factory pattern, allowing multiple
instances with different configurations.
"""

import logging
from typing import Optional

from quart import Quart
from quart_schema import QuartSchema, Info, Tag

from .config import config


async def create_app(config_name: str = "development") -> Quart:
    """Create and configure the Quart application.

    Args:
        config_name: Configuration environment name (development, testing, production)

    Returns:
        Configured Quart application instance
    """
    # Initialize Quart app
    app = Quart(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    app.config.from_prefixed_env()  # Override with QUART_ env vars

    # Configure logging
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format=app.config["LOG_FORMAT"],
    )

    # Initialize extensions
    await init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Application lifecycle hooks
    register_lifecycle_hooks(app)

    return app


async def init_extensions(app: Quart) -> None:
    """Initialize Quart extensions.

    Args:
        app: Quart application instance
    """
    # Initialize Quart-Schema for validation and OpenAPI docs
    QuartSchema(
        app,
        info=Info(
            title="Quart API",
            version="1.0.0",
            description="RESTful API built with Quart",
        ),
        tags=[
            Tag(name="auth", description="Authentication endpoints"),
            Tag(name="items", description="Item management endpoints"),
            Tag(name="websocket", description="WebSocket endpoints"),
        ],
    )

    # Initialize database
    from .models import init_db

    await init_db(app)


def register_blueprints(app: Quart) -> None:
    """Register application blueprints.

    Args:
        app: Quart application instance
    """
    from .routes.api import api_bp
    from .routes.auth import auth_bp
    from .routes.ws import ws_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(ws_bp, url_prefix="/ws")


def register_error_handlers(app: Quart) -> None:
    """Register global error handlers.

    Args:
        app: Quart application instance
    """

    @app.errorhandler(400)
    async def bad_request(error):
        """Handle 400 Bad Request errors."""
        return {"error": "Bad Request", "message": str(error)}, 400

    @app.errorhandler(401)
    async def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        return {"error": "Unauthorized", "message": "Authentication required"}, 401

    @app.errorhandler(404)
    async def not_found(error):
        """Handle 404 Not Found errors."""
        return {"error": "Not Found", "message": "Resource not found"}, 404

    @app.errorhandler(500)
    async def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        app.logger.error(f"Internal server error: {error}")
        return {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        }, 500


def register_lifecycle_hooks(app: Quart) -> None:
    """Register application lifecycle hooks.

    Args:
        app: Quart application instance
    """

    @app.before_serving
    async def startup():
        """Execute before the application starts serving requests."""
        app.logger.info("Application startup complete")

    @app.after_serving
    async def shutdown():
        """Execute after the application stops serving requests."""
        app.logger.info("Application shutdown complete")

        # Close database connections
        if hasattr(app, "db_engine"):
            await app.db_engine.dispose()


# Default app instance for simple usage (Hypercorn CLI, testing)
# This allows using both 'src.app:app' and 'src.app:create_app()' patterns
app = Quart(__name__)


async def _init_app():
    """Initialize the default app instance."""
    global app
    app = await create_app()


# Note: In production, use create_app() with explicit config:
# hypercorn "src.app:create_app('production')" --bind 0.0.0.0:8000
