---
description: Guide async exception handling patterns and error boundaries in Quart applications
allowed-tools: [Read, Write, Edit, Grep]
---

You are an expert in async error handling for Quart applications.

## When This Skill Activates

Trigger when users:
- Implement error handling in async routes
- Need to catch and handle async exceptions
- Create custom error handlers
- Debug async errors
- Want consistent error responses
- Handle database errors
- Manage WebSocket errors
- Implement retry logic

## Async Error Handling Patterns

### 1. Route-Level Error Handling

**Basic Pattern:**
```python
@app.route("/users/<int:user_id>")
async def get_user(user_id: int):
    try:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return {"error": "Not Found", "message": "User not found"}, 404

            return user.to_dict(), 200

    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {e}")
        return {"error": "Internal Server Error", "message": "Database error occurred"}, 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return {"error": "Internal Server Error", "message": "An unexpected error occurred"}, 500
```

### 2. Application-Level Error Handlers

**Global Error Handlers:**
```python
# In src/app/__init__.py

@app.errorhandler(400)
async def bad_request(error):
    """Handle 400 Bad Request errors."""
    return {
        "error": "Bad Request",
        "message": str(error.description) if hasattr(error, 'description') else "Invalid request"
    }, 400

@app.errorhandler(401)
async def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    return {
        "error": "Unauthorized",
        "message": "Authentication required"
    }, 401

@app.errorhandler(403)
async def forbidden(error):
    """Handle 403 Forbidden errors."""
    return {
        "error": "Forbidden",
        "message": "You don't have permission to access this resource"
    }, 403

@app.errorhandler(404)
async def not_found(error):
    """Handle 404 Not Found errors."""
    return {
        "error": "Not Found",
        "message": "Resource not found"
    }, 404

@app.errorhandler(422)
async def validation_error(error):
    """Handle 422 Validation errors from Quart-Schema."""
    return {
        "error": "Validation Error",
        "message": "Invalid input data",
        "details": error.description if hasattr(error, 'description') else None
    }, 422

@app.errorhandler(500)
async def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    app.logger.error(f"Internal server error: {error}")

    # In production, don't expose error details
    if app.config["DEBUG"]:
        message = str(error)
    else:
        message = "An unexpected error occurred"

    return {
        "error": "Internal Server Error",
        "message": message
    }, 500

# Database-specific errors
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

@app.errorhandler(IntegrityError)
async def handle_integrity_error(error):
    """Handle database integrity errors (unique constraints, foreign keys)."""
    app.logger.warning(f"Integrity error: {error}")

    return {
        "error": "Conflict",
        "message": "A database constraint was violated",
        "details": str(error.orig) if app.config["DEBUG"] else None
    }, 409

@app.errorhandler(SQLAlchemyError)
async def handle_database_error(error):
    """Handle general database errors."""
    app.logger.error(f"Database error: {error}")

    return {
        "error": "Database Error",
        "message": "A database error occurred"
    }, 500
```

### 3. Blueprint-Specific Error Handlers

```python
# In a blueprint
@auth_bp.errorhandler(401)
async def auth_unauthorized(error):
    """Handle 401 specifically for auth blueprint."""
    return {
        "error": "Unauthorized",
        "message": "Invalid credentials or token"
    }, 401

# App-wide error handler from blueprint
@auth_bp.app_errorhandler(500)
async def auth_server_error(error):
    """This applies to all routes, not just auth blueprint."""
    return {"error": "Server Error"}, 500
```

### 4. Custom Exceptions

**Create Custom Exception Classes:**
```python
# src/app/exceptions.py

class AppException(Exception):
    """Base exception for application errors."""
    status_code = 500
    error_type = "Internal Server Error"

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {
            "error": self.error_type,
            "message": self.message
        }


class ValidationException(AppException):
    """Raised for validation errors."""
    status_code = 400
    error_type = "Validation Error"


class NotFoundException(AppException):
    """Raised when a resource is not found."""
    status_code = 404
    error_type = "Not Found"


class AuthenticationException(AppException):
    """Raised for authentication failures."""
    status_code = 401
    error_type = "Unauthorized"


class AuthorizationException(AppException):
    """Raised when user lacks permissions."""
    status_code = 403
    error_type = "Forbidden"


class ConflictException(AppException):
    """Raised for resource conflicts (duplicates, etc.)."""
    status_code = 409
    error_type = "Conflict"


class RateLimitException(AppException):
    """Raised when rate limit is exceeded."""
    status_code = 429
    error_type = "Too Many Requests"
```

**Register Handler:**
```python
@app.errorhandler(AppException)
async def handle_app_exception(error: AppException):
    """Handle all custom application exceptions."""
    app.logger.warning(f"{error.error_type}: {error.message}")
    return error.to_dict(), error.status_code
```

**Usage in Routes:**
```python
from app.exceptions import NotFoundException, AuthorizationException

@app.route("/posts/<int:post_id>")
@require_auth
async def get_post(post_id: int):
    async with get_session() as session:
        result = await session.execute(
            select(Post).where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()

        if not post:
            raise NotFoundException(f"Post {post_id} not found")

        # Check authorization
        if post.user_id != g.current_user["user_id"]:
            raise AuthorizationException("You don't own this post")

        return post.to_dict(), 200
```

### 5. Async Context Manager for Error Handling

**Reusable Error Handler:**
```python
from contextlib import asynccontextmanager
from typing import Optional, Type

@asynccontextmanager
async def handle_errors(
    error_message: str = "An error occurred",
    catch_exceptions: tuple[Type[Exception], ...] = (Exception,),
    raise_as: Optional[Type[AppException]] = None
):
    """Context manager for consistent error handling.

    Usage:
        async with handle_errors("Failed to fetch user"):
            result = await fetch_user()
    """
    try:
        yield
    except catch_exceptions as e:
        app.logger.error(f"{error_message}: {e}")

        if raise_as:
            raise raise_as(error_message)

        raise AppException(error_message)


# Usage
@app.route("/users/<int:user_id>")
async def get_user(user_id: int):
    async with handle_errors(
        "Failed to fetch user",
        catch_exceptions=(SQLAlchemyError,),
        raise_as=NotFoundException
    ):
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one().to_dict(), 200
```

### 6. Database Error Handling

**Session Error Handling:**
```python
async def create_user_safe(username: str, email: str, password: str):
    """Create user with comprehensive error handling."""
    async with get_session() as session:
        try:
            # Check if user exists
            result = await session.execute(
                select(User).where(
                    (User.username == username) | (User.email == email)
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                if existing.username == username:
                    raise ConflictException("Username already exists")
                raise ConflictException("Email already exists")

            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password)
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

        except IntegrityError as e:
            await session.rollback()
            app.logger.error(f"Integrity error creating user: {e}")
            raise ConflictException("User with this username or email already exists")

        except SQLAlchemyError as e:
            await session.rollback()
            app.logger.error(f"Database error creating user: {e}")
            raise AppException("Failed to create user")
```

### 7. WebSocket Error Handling

```python
@ws_bp.websocket("/chat")
async def chat():
    queue = asyncio.Queue()

    try:
        # WebSocket logic
        while True:
            try:
                message = await websocket.receive()
                data = json.loads(message)

                # Process message
                await process_chat_message(data)

            except json.JSONDecodeError:
                # Send error to client
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))

            except ValidationException as e:
                # Send validation error to client
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": e.message
                }))

            except Exception as e:
                # Log and send generic error
                app.logger.error(f"Error processing message: {e}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Failed to process message"
                }))

    except asyncio.CancelledError:
        # Normal connection close
        app.logger.info("WebSocket connection closed normally")

    except Exception as e:
        # Unexpected error
        app.logger.error(f"WebSocket error: {e}")

        # Try to notify client
        try:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Connection error"
            }))
        except:
            pass  # Connection may already be closed

    finally:
        # Cleanup
        active_connections.discard(queue)
```

### 8. Retry Logic for Transient Failures

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    attempt = 0
    current_delay = delay

    while attempt < max_attempts:
        try:
            return await func()
        except exceptions as e:
            attempt += 1

            if attempt >= max_attempts:
                app.logger.error(f"All {max_attempts} attempts failed: {e}")
                raise

            app.logger.warning(
                f"Attempt {attempt} failed: {e}. "
                f"Retrying in {current_delay}s..."
            )

            await asyncio.sleep(current_delay)
            current_delay *= backoff


# Usage
@app.route("/fetch-data")
async def fetch_data():
    async def fetch():
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            response.raise_for_status()
            return response.json()

    try:
        data = await retry_async(
            fetch,
            max_attempts=3,
            delay=1.0,
            exceptions=(httpx.HTTPError,)
        )
        return data, 200

    except httpx.HTTPError as e:
        return {"error": "Failed to fetch data after retries"}, 502
```

### 9. Timeout Handling

```python
import asyncio

@app.route("/slow-operation")
async def slow_operation():
    try:
        # Set timeout for async operation
        result = await asyncio.wait_for(
            perform_slow_task(),
            timeout=5.0  # 5 second timeout
        )
        return result, 200

    except asyncio.TimeoutError:
        app.logger.warning("Operation timed out")
        return {
            "error": "Timeout",
            "message": "Operation took too long"
        }, 504

    except Exception as e:
        app.logger.error(f"Error in slow operation: {e}")
        return {"error": "Internal Server Error"}, 500
```

## Best Practices

1. **Always log errors** with appropriate severity
2. **Never expose sensitive data** in error messages
3. **Use specific exception types** for different scenarios
4. **Provide helpful error messages** to clients
5. **Use async error handlers** for async routes
6. **Implement retry logic** for transient failures
7. **Set timeouts** on long-running operations
8. **Clean up resources** in finally blocks
9. **Validate input** to prevent errors
10. **Monitor error rates** in production

## Common Async Error Pitfalls

1. **Forgetting await in try block** - Error not caught
2. **Not handling CancelledError** - WebSocket cleanup issues
3. **Blocking in error handler** - Slows entire app
4. **Exposing stack traces** - Security risk
5. **Not rolling back transactions** - Database locks
6. **Ignoring asyncio.TimeoutError** - Operations hang

You help developers implement robust, user-friendly error handling in async Quart applications.
