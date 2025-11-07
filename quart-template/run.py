"""Development server runner.

Quick way to run the application without setting QUART_APP environment variable.

Usage:
    python run.py

This is equivalent to:
    QUART_APP="src.app:create_app()" quart run --reload
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import create_app


async def main():
    """Run the development server."""
    app = await create_app("development")

    print("\n" + "=" * 60)
    print("Quart Development Server")
    print("=" * 60)
    print(f"Environment: {app.config.get('QUART_ENV', 'development')}")
    print(f"Debug: {app.config.get('DEBUG', False)}")
    print(f"Database: {app.config.get('DATABASE_URL', 'not configured')}")
    print("\nServer starting at: http://127.0.0.1:5000")
    print("\nAPI Documentation:")
    print("  - Swagger UI: http://127.0.0.1:5000/docs")
    print("  - ReDoc:      http://127.0.0.1:5000/redocs")
    print("  - Scalar:     http://127.0.0.1:5000/scalar")
    print("\nPress CTRL+C to stop")
    print("=" * 60 + "\n")

    # Run with reload
    await app.run_task(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
