"""APScheduler engine with SQLite job store."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from apscheduler.executors.pool import ThreadPoolExecutor as APSThreadPool
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from agent.config import settings
from agent.utils.logging import get_logger

logger = get_logger(__name__)

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        settings.ensure_data_dir()
        jobstores = {
            "default": SQLAlchemyJobStore(url=settings.scheduler_db_url)
        }
        executors = {
            "default": APSThreadPool(max_workers=settings.worker_threads)
        }
        _scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 60},
            timezone="UTC",
        )
    return _scheduler


def start_scheduler() -> None:
    sched = get_scheduler()
    if not sched.running:
        sched.start()
        logger.info("Scheduler started")


def stop_scheduler() -> None:
    sched = get_scheduler()
    if sched.running:
        sched.shutdown(wait=True)
        logger.info("Scheduler stopped")


def add_job(
    task_type: str,
    trigger_str: str,
    config: dict[str, Any],
    job_id: str | None = None,
) -> str:
    """Add a task job to the scheduler. Returns the job ID."""
    from agent.scheduler.triggers import parse_trigger
    from agent.scheduler.registry import get_task_class

    # Validate task type exists
    get_task_class(task_type)

    trigger = parse_trigger(trigger_str)
    sched = get_scheduler()

    # Stable job ID based on type+config if not supplied
    if job_id is None:
        try:
            from agent_core_ext import hash_task_id  # type: ignore[import]
        except ImportError:
            import hashlib

            def hash_task_id(s: str) -> str:
                return hashlib.sha256(s.encode()).hexdigest()[:16]

        payload = json.dumps({"type": task_type, "config": config}, sort_keys=True)
        job_id = f"{task_type}-{hash_task_id(payload)[:8]}"

    def _run_task():
        _execute_task(task_type, job_id, config)

    sched.add_job(
        _run_task,
        trigger=trigger,
        id=job_id,
        replace_existing=True,
        name=f"{task_type}:{job_id}",
    )
    logger.info("Scheduled job %s (type=%s)", job_id, task_type)
    return job_id


def _execute_task(task_type: str, job_id: str, config: dict[str, Any]) -> None:
    """Internal: instantiate and run a task, persisting the result."""
    from agent.scheduler.registry import get_task_class
    from agent.db.session import get_session
    from agent.db.models import TaskRun

    started = datetime.utcnow()
    task_cls = get_task_class(task_type)
    task = task_cls(config)

    with get_session() as session:
        run = TaskRun(job_id=job_id, task_type=task_type, status="running", started_at=started)
        session.add(run)
        session.flush()
        run_id = run.id

    try:
        result = task.run()
        with get_session() as session:
            run = session.get(TaskRun, run_id)
            if run:
                run.status = result.status
                run.result_json = json.dumps(result.data)
                run.finished_at = datetime.utcnow()
    except Exception as exc:
        logger.exception("Task %s failed: %s", job_id, exc)
        with get_session() as session:
            run = session.get(TaskRun, run_id)
            if run:
                run.status = "error"
                run.error_message = str(exc)
                run.finished_at = datetime.utcnow()


def remove_job(job_id: str) -> bool:
    sched = get_scheduler()
    try:
        sched.remove_job(job_id)
        return True
    except Exception:
        return False


def list_jobs() -> list[dict[str, Any]]:
    sched = get_scheduler()
    jobs = []
    for job in sched.get_jobs():
        nxt = job.next_run_time
        jobs.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run": nxt.isoformat() if nxt else None,
            }
        )
    return jobs


def run_job_now(job_id: str) -> bool:
    sched = get_scheduler()
    job = sched.get_job(job_id)
    if not job:
        return False
    job.modify(next_run_time=datetime.utcnow())
    return True
