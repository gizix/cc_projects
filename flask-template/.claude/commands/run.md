---
description: Start Flask development server
argument-hint: "[--port PORT] [--host HOST] [--debug]"
---

Start the Flask development server.

## Arguments

- `--port PORT`: Port to run on (default: 5000)
- `--host HOST`: Host to bind to (default: 127.0.0.1)
- `--debug`: Enable debug mode

## Examples

```bash
# Start server on default port 5000
flask run

# Start on custom port
flask run --port 8080

# Start with public access
flask run --host 0.0.0.0

# Start in debug mode
flask run --debug
```

## Notes

- The development server should not be used in production
- Use `gunicorn` or another WSGI server for production deployments
- Debug mode enables auto-reload and detailed error pages

Execute: `cd flask-template && flask run $ARGUMENTS`
