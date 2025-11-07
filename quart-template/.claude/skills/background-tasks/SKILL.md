---
description: Guide implementation of long-running async tasks and lifecycle management in Quart
allowed-tools: [Read, Write, Edit, Grep]
---

You are an expert in async background tasks and application lifecycle management in Quart.

## When This Skill Activates

Trigger when users:
- Need to run background tasks
- Implement periodic tasks
- Handle long-running operations
- Set up application startup/shutdown
- Manage async task lifecycles
- Queue jobs for processing
- Implement worker patterns
- Debug background task issues

## Background Task Patterns

### 1. Simple Background Task

```python
from quart import Quart

app = Quart(__name__)

async def send_email_async(to: str, subject: str, body: str):
    """Send an email asynchronously."""
    await asyncio.sleep(2)  # Simulate email sending
    app.logger.info(f"Email sent to {to}: {subject}")


@app.route("/register", methods=["POST"])
async def register():
    # ... create user ...

    # Add background task (doesn't block response)
    app.add_background_task(send_email_async, user.email, "Welcome!", "Thanks for registering")

    return {"message": "User registered", "user_id": user.id}, 201
```

**Key Points:**
- `add_background_task()` returns immediately
- Task runs after response is sent
- Exceptions in tasks are logged but don't affect response

### 2. Application Lifecycle Hooks

```python
@app.before_serving
async def startup():
    """Execute before the application starts serving requests."""
    app.logger.info("Application starting up...")

    # Initialize connections
    app.redis = await aioredis.create_redis_pool("redis://localhost")
    app.http_client = httpx.AsyncClient()

    # Start background workers
    app.add_background_task(periodic_cleanup())
    app.add_background_task(metrics_collector())

    app.logger.info("Application startup complete")


@app.after_serving
async def shutdown():
    """Execute after the application stops serving requests."""
    app.logger.info("Application shutting down...")

    # Close connections
    if hasattr(app, 'redis'):
        app.redis.close()
        await app.redis.wait_closed()

    if hasattr(app, 'http_client'):
        await app.http_client.aclose()

    # Close database
    if hasattr(app, 'db_engine'):
        await app.db_engine.dispose()

    app.logger.info("Application shutdown complete")


@app.while_serving
async def lifespan():
    """Context manager pattern for resources."""
    # Acquire resources
    resource = await acquire_resource()
    app.resource = resource

    yield  # Application serves requests

    # Release resources
    await release_resource(resource)
```

### 3. Periodic Tasks

```python
async def periodic_cleanup():
    """Run cleanup task every hour."""
    while True:
        try:
            app.logger.info("Running periodic cleanup...")

            # Perform cleanup
            async with get_session() as session:
                # Delete old expired tokens
                await session.execute(
                    delete(Token).where(Token.expires_at < datetime.utcnow())
                )
                await session.commit()

            app.logger.info("Cleanup complete")

        except Exception as e:
            app.logger.error(f"Cleanup error: {e}")

        # Wait until next run
        await asyncio.sleep(3600)  # 1 hour


async def metrics_collector():
    """Collect metrics every 30 seconds."""
    while True:
        try:
            # Collect metrics
            metrics = await collect_application_metrics()

            # Send to monitoring service
            await send_metrics(metrics)

        except Exception as e:
            app.logger.error(f"Metrics collection error: {e}")

        await asyncio.sleep(30)


@app.before_serving
async def startup():
    # Start periodic tasks
    app.add_background_task(periodic_cleanup())
    app.add_background_task(metrics_collector())
```

### 4. Task Queue with asyncio.Queue

```python
import asyncio
from typing import Callable, Any

# Global task queue
task_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)


async def worker(worker_id: int):
    """Worker that processes tasks from queue."""
    app.logger.info(f"Worker {worker_id} started")

    while True:
        try:
            # Get task from queue
            task_func, args, kwargs = await task_queue.get()

            app.logger.info(f"Worker {worker_id} processing task: {task_func.__name__}")

            try:
                # Execute task
                await task_func(*args, **kwargs)

            except Exception as e:
                app.logger.error(f"Task {task_func.__name__} failed: {e}")

            finally:
                task_queue.task_done()

        except asyncio.CancelledError:
            app.logger.info(f"Worker {worker_id} cancelled")
            break

        except Exception as e:
            app.logger.error(f"Worker {worker_id} error: {e}")


async def enqueue_task(func: Callable, *args: Any, **kwargs: Any):
    """Add a task to the queue."""
    try:
        await task_queue.put((func, args, kwargs))
        app.logger.info(f"Task {func.__name__} enqueued")

    except asyncio.QueueFull:
        app.logger.error(f"Task queue full, dropping task {func.__name__}")
        raise Exception("Task queue is full")


@app.before_serving
async def startup():
    """Start worker pool."""
    # Start multiple workers
    num_workers = 4

    for i in range(num_workers):
        app.add_background_task(worker(i))

    app.logger.info(f"Started {num_workers} workers")


# Usage in routes
@app.route("/process", methods=["POST"])
async def process_data():
    data = await request.get_json()

    # Enqueue task for background processing
    await enqueue_task(process_data_async, data)

    return {"message": "Task queued for processing"}, 202
```

### 5. Task with Timeout

```python
import asyncio

async def task_with_timeout(timeout: float = 30.0):
    """Run a task with timeout."""
    try:
        result = await asyncio.wait_for(
            long_running_operation(),
            timeout=timeout
        )
        return result

    except asyncio.TimeoutError:
        app.logger.warning(f"Task timed out after {timeout}s")
        # Cleanup or retry logic
        raise


async def long_running_operation():
    """Simulate long operation."""
    await asyncio.sleep(60)  # Long operation
    return "Result"


# Configure timeout in config
class Config:
    BACKGROUND_TASK_SHUTDOWN_TIMEOUT = 30  # seconds


@app.after_serving
async def shutdown():
    """Shutdown with timeout for background tasks."""
    # Quart automatically awaits background tasks with configured timeout
    pass
```

### 6. Task Cancellation

```python
from typing import Dict

# Store running tasks
running_tasks: Dict[str, asyncio.Task] = {}


async def cancellable_task(task_id: str):
    """Task that can be cancelled."""
    try:
        while True:
            # Check if task should continue
            if task_id not in running_tasks:
                app.logger.info(f"Task {task_id} cancelled")
                break

            # Do work
            await asyncio.sleep(1)
            app.logger.info(f"Task {task_id} working...")

    except asyncio.CancelledError:
        app.logger.info(f"Task {task_id} was cancelled")
        # Cleanup
        raise

    finally:
        running_tasks.pop(task_id, None)


@app.route("/tasks/start", methods=["POST"])
async def start_task():
    """Start a cancellable task."""
    task_id = str(uuid.uuid4())

    # Create and store task
    task = asyncio.create_task(cancellable_task(task_id))
    running_tasks[task_id] = task

    return {"task_id": task_id, "status": "started"}, 202


@app.route("/tasks/<task_id>/cancel", methods=["POST"])
async def cancel_task(task_id: str):
    """Cancel a running task."""
    task = running_tasks.get(task_id)

    if not task:
        return {"error": "Task not found"}, 404

    # Cancel the task
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    return {"task_id": task_id, "status": "cancelled"}, 200


@app.route("/tasks/<task_id>/status", methods=["GET"])
async def task_status(task_id: str):
    """Check task status."""
    task = running_tasks.get(task_id)

    if not task:
        return {"task_id": task_id, "status": "not_found"}, 404

    if task.done():
        status = "completed" if not task.cancelled() else "cancelled"
    else:
        status = "running"

    return {"task_id": task_id, "status": status}, 200
```

### 7. Rate-Limited Background Processing

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """Token bucket rate limiter for async operations."""

    def __init__(self, rate: float, per: float):
        """
        Args:
            rate: Number of operations
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = datetime.now()

    async def acquire(self):
        """Wait until rate limit allows operation."""
        while True:
            now = datetime.now()
            time_passed = (now - self.last_check).total_seconds()
            self.last_check = now

            self.allowance += time_passed * (self.rate / self.per)
            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance >= 1.0:
                self.allowance -= 1.0
                break

            # Wait before retry
            await asyncio.sleep(0.1)


# Usage
rate_limiter = RateLimiter(rate=10, per=1.0)  # 10 operations per second


async def rate_limited_api_call(url: str):
    """Make API call with rate limiting."""
    await rate_limiter.acquire()

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


async def process_urls_batch(urls: list[str]):
    """Process multiple URLs with rate limiting."""
    tasks = [rate_limited_api_call(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

### 8. Batch Processing Worker

```python
async def batch_processor():
    """Process items in batches."""
    batch_size = 100
    batch_interval = 5  # seconds

    pending_items = []

    while True:
        try:
            # Collect items for batch
            try:
                # Wait for items with timeout
                item = await asyncio.wait_for(
                    task_queue.get(),
                    timeout=batch_interval
                )
                pending_items.append(item)

                # Continue collecting until batch size or timeout
                while len(pending_items) < batch_size:
                    try:
                        item = await asyncio.wait_for(
                            task_queue.get(),
                            timeout=0.1
                        )
                        pending_items.append(item)
                    except asyncio.TimeoutError:
                        break

            except asyncio.TimeoutError:
                pass  # Process whatever we have

            # Process batch
            if pending_items:
                app.logger.info(f"Processing batch of {len(pending_items)} items")

                try:
                    await process_batch(pending_items)
                except Exception as e:
                    app.logger.error(f"Batch processing error: {e}")

                pending_items.clear()

        except asyncio.CancelledError:
            # Process remaining items before shutdown
            if pending_items:
                await process_batch(pending_items)
            break

        except Exception as e:
            app.logger.error(f"Batch processor error: {e}")
            await asyncio.sleep(1)


async def process_batch(items: list):
    """Process a batch of items."""
    # Implement batch processing logic
    async with get_session() as session:
        for item in items:
            # Process item
            pass
        await session.commit()
```

### 9. Graceful Shutdown

```python
import signal

shutdown_event = asyncio.Event()


def handle_shutdown(signum, frame):
    """Signal handler for graceful shutdown."""
    app.logger.info(f"Received signal {signum}, initiating shutdown...")
    shutdown_event.set()


@app.before_serving
async def setup_signals():
    """Set up signal handlers."""
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)


async def long_running_worker():
    """Worker that respects shutdown signal."""
    while not shutdown_event.is_set():
        try:
            # Do work with timeout to check shutdown periodically
            await asyncio.wait_for(
                process_next_item(),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            continue  # Check shutdown event
        except Exception as e:
            app.logger.error(f"Worker error: {e}")

    app.logger.info("Worker shutting down gracefully")


@app.after_serving
async def shutdown():
    """Shutdown with grace period."""
    # Set shutdown event
    shutdown_event.set()

    # Wait for workers to finish (with timeout)
    grace_period = app.config.get("BACKGROUND_TASK_SHUTDOWN_TIMEOUT", 30)

    try:
        await asyncio.wait_for(
            wait_for_workers(),
            timeout=grace_period
        )
    except asyncio.TimeoutError:
        app.logger.warning("Some workers did not finish within grace period")
```

### 10. Progress Tracking

```python
from typing import Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TaskProgress:
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 to 1.0
    message: str
    created_at: datetime
    updated_at: datetime
    result: Any = None
    error: str = None


task_progress: Dict[str, TaskProgress] = {}


async def tracked_task(task_id: str, items: list):
    """Task with progress tracking."""
    total = len(items)

    task_progress[task_id] = TaskProgress(
        task_id=task_id,
        status="running",
        progress=0.0,
        message="Starting task",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        for i, item in enumerate(items):
            # Process item
            await process_item(item)

            # Update progress
            progress = (i + 1) / total
            task_progress[task_id].progress = progress
            task_progress[task_id].message = f"Processed {i + 1}/{total} items"
            task_progress[task_id].updated_at = datetime.utcnow()

        # Mark complete
        task_progress[task_id].status = "completed"
        task_progress[task_id].progress = 1.0
        task_progress[task_id].message = "Task completed successfully"

    except Exception as e:
        task_progress[task_id].status = "failed"
        task_progress[task_id].error = str(e)
        app.logger.error(f"Task {task_id} failed: {e}")


@app.route("/tasks/<task_id>/progress", methods=["GET"])
async def get_task_progress(task_id: str):
    """Get task progress."""
    progress = task_progress.get(task_id)

    if not progress:
        return {"error": "Task not found"}, 404

    return {
        "task_id": progress.task_id,
        "status": progress.status,
        "progress": progress.progress,
        "message": progress.message,
        "created_at": progress.created_at.isoformat(),
        "updated_at": progress.updated_at.isoformat(),
        "error": progress.error
    }, 200
```

## Best Practices

1. **Always handle exceptions** in background tasks
2. **Set timeouts** for long-running operations
3. **Implement graceful shutdown** with cleanup
4. **Use queues** for work distribution
5. **Track task status** for long operations
6. **Rate limit** external API calls
7. **Batch process** when possible for efficiency
8. **Log task execution** for debugging
9. **Make tasks idempotent** when possible
10. **Configure shutdown timeout** appropriately

## Common Pitfalls

1. **Blocking calls** in async tasks (use async libraries)
2. **Memory leaks** from tasks never completing
3. **No timeout** on long operations
4. **Unhandled exceptions** crashing workers
5. **Resource leaks** (connections not closed)
6. **No progress tracking** for long tasks
7. **Ignoring cancellation** signals

You help developers implement reliable, efficient background task processing in Quart applications.
