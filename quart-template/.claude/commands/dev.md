---
description: Run Hypercorn development server with hot-reload
argument-hint: [--port PORT]
allowed-tools: Bash(*)
model: sonnet
---

Start the Quart development server with hot-reload enabled using Hypercorn.

## Arguments

- `$1`: Port number (optional, defaults to 5000)

## Usage

- `/dev` - Start on default port 5000
- `/dev 8080` - Start on custom port 8080

## What This Does

1. Starts Hypercorn ASGI server
2. Enables auto-reload on code changes
3. Binds to 0.0.0.0 (accessible from network)
4. Loads the Quart app using the factory pattern

## Command

```bash
PORT=${1:-5000}
echo "Starting Quart development server on port $PORT..."
export QUART_APP="src.app:create_app()"
hypercorn "$QUART_APP" --bind 0.0.0.0:$PORT --reload
```

## Notes

- Press Ctrl+C to stop the server
- Hot-reload watches for Python file changes
- Access API documentation at http://localhost:$PORT/docs
- Health check available at http://localhost:$PORT/health
