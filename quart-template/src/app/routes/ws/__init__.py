"""WebSocket blueprint.

This blueprint demonstrates Quart's native WebSocket support with
authentication and message handling.
"""

import asyncio
import json
from datetime import datetime
from typing import Set

from quart import Blueprint, websocket, current_app
from quart_schema import validate_websocket

from ...schemas import WebSocketMessageSchema
from ...auth import decode_token

ws_bp = Blueprint("ws", __name__)

# Active WebSocket connections
active_connections: Set[asyncio.Queue] = set()


@ws_bp.websocket("/echo")
async def echo():
    """Simple echo WebSocket endpoint.

    Echoes back any message received from the client.
    No authentication required.
    """
    try:
        while True:
            message = await websocket.receive()
            await websocket.send(f"Echo: {message}")
    except asyncio.CancelledError:
        # Connection closed
        pass


@ws_bp.websocket("/chat")
async def chat():
    """Multi-client chat WebSocket endpoint.

    Broadcasts messages to all connected clients.
    Requires authentication via JWT token in first message.
    """
    # Create queue for this connection
    queue: asyncio.Queue = asyncio.Queue()
    active_connections.add(queue)

    username = "Anonymous"
    authenticated = False

    try:
        # Receive first message with authentication token
        first_message = await websocket.receive()

        try:
            auth_data = json.loads(first_message)
            if "token" in auth_data:
                payload = decode_token(auth_data["token"])
                if payload and payload.get("type") == "access":
                    username = payload["username"]
                    authenticated = True
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "auth",
                                "success": True,
                                "username": username,
                                "message": "Authentication successful",
                            }
                        )
                    )
                else:
                    await websocket.send(
                        json.dumps(
                            {"type": "auth", "success": False, "message": "Invalid token"}
                        )
                    )
                    return
        except json.JSONDecodeError:
            await websocket.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": "First message must be JSON with 'token' field",
                    }
                )
            )
            return

        # Broadcast join message
        join_message = {
            "type": "system",
            "message": f"{username} joined the chat",
            "timestamp": datetime.utcnow().isoformat(),
        }
        await broadcast_message(json.dumps(join_message), exclude=queue)

        # Create tasks for sending and receiving
        async def receive_messages():
            """Receive messages from this client and broadcast."""
            while True:
                message = await websocket.receive()

                try:
                    data = json.loads(message)
                    broadcast_data = {
                        "type": "message",
                        "username": username,
                        "message": data.get("message", ""),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await broadcast_message(json.dumps(broadcast_data))
                except json.JSONDecodeError:
                    await websocket.send(
                        json.dumps({"type": "error", "message": "Invalid JSON"})
                    )

        async def send_messages():
            """Send queued messages to this client."""
            while True:
                message = await queue.get()
                await websocket.send(message)

        # Run both tasks concurrently
        await asyncio.gather(receive_messages(), send_messages())

    except asyncio.CancelledError:
        # Connection closed
        pass
    finally:
        # Clean up
        active_connections.discard(queue)

        # Broadcast leave message
        leave_message = {
            "type": "system",
            "message": f"{username} left the chat",
            "timestamp": datetime.utcnow().isoformat(),
        }
        await broadcast_message(json.dumps(leave_message))


@ws_bp.websocket("/notifications")
async def notifications():
    """Real-time notifications WebSocket.

    Sends periodic notifications to authenticated clients.
    Requires JWT token in query parameter: /ws/notifications?token=<jwt>
    """
    # Get token from query parameter
    from quart import request

    token = request.args.get("token")

    if not token:
        await websocket.send(
            json.dumps({"type": "error", "message": "Token required in query parameter"})
        )
        return

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.send(json.dumps({"type": "error", "message": "Invalid token"}))
        return

    username = payload["username"]

    try:
        # Send welcome message
        await websocket.send(
            json.dumps(
                {
                    "type": "welcome",
                    "message": f"Welcome {username}! Connected to notifications",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        # Send periodic notifications
        counter = 0
        while True:
            await asyncio.sleep(10)  # Send notification every 10 seconds
            counter += 1

            notification = {
                "type": "notification",
                "id": counter,
                "message": f"Periodic notification #{counter}",
                "timestamp": datetime.utcnow().isoformat(),
            }

            await websocket.send(json.dumps(notification))

    except asyncio.CancelledError:
        current_app.logger.info(f"Notification connection closed for {username}")


async def broadcast_message(message: str, exclude: asyncio.Queue = None):
    """Broadcast a message to all connected clients.

    Args:
        message: Message to broadcast
        exclude: Optional queue to exclude from broadcast
    """
    for connection_queue in active_connections:
        if connection_queue != exclude:
            await connection_queue.put(message)
