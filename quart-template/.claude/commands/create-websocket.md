---
description: Add WebSocket endpoint
argument-hint: "<endpoint-path> [auth-required]"
---

Create a new WebSocket endpoint in the ws blueprint.

Arguments:
- $1: WebSocket path (e.g., "notifications", "live-updates")
- $2: Authentication required? (yes/no, default: yes)

I'll create a WebSocket endpoint at `/ws/$1`.

Steps I'll take:
1. Add WebSocket handler to `src/app/routes/ws/__init__.py`
2. Implement connection handling with asyncio
3. Add message sending/receiving logic
4. Include authentication if required
5. Add proper error handling and cleanup
6. Support graceful connection closure

Example WebSocket patterns I can implement:
- Echo server (simple message echo)
- Broadcast (send to all connected clients)
- One-to-one (private messages)
- Notifications (server → client only)

Authentication methods:
- Token in first message (JSON: {"token": "jwt"})
- Token in query parameter (?token=jwt)
- No authentication (public endpoint)

Would you like me to proceed with creating this WebSocket endpoint?
