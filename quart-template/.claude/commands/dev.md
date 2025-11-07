---
description: Start development server with hot reload
---

Start the Quart development server with hot reloading enabled.

Run the following command:

```bash
cd quart-template && QUART_APP="src.app:create_app()" quart run --reload
```

The development server will start on http://localhost:5000 with:
- Hot reload enabled (automatically restarts on code changes)
- Debug mode active
- Detailed error pages
- Development configuration loaded

You can access:
- API endpoints at http://localhost:5000/api
- Health check at http://localhost:5000/api/health
- OpenAPI docs at http://localhost:5000/docs
- WebSocket endpoints at ws://localhost:5000/ws
