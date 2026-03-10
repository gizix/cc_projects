"""FastAPI web dashboard — runs in a daemon thread alongside the scheduler."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Autonomous Agent Dashboard", docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scheduler_status() -> dict[str, Any]:
    try:
        from agent.scheduler.engine import get_scheduler, list_jobs
        from agent.utils.threading import active_count

        sched = get_scheduler()
        jobs = list_jobs()
        return {
            "running": sched.running,
            "worker_active": active_count(),
            "job_count": len(jobs),
            "next_fires": jobs[:5],
        }
    except Exception as e:
        return {"running": False, "error": str(e)}


def _recent_runs(limit: int = 10) -> list[dict]:
    try:
        from agent.db.session import get_session
        from agent.db.models import TaskRun
        from sqlalchemy import select

        with get_session() as session:
            stmt = select(TaskRun).order_by(TaskRun.started_at.desc()).limit(limit)
            runs = session.execute(stmt).scalars().all()
            return [
                {
                    "id": r.id,
                    "job_id": r.job_id,
                    "task_type": r.task_type,
                    "status": r.status,
                    "started_at": r.started_at.isoformat() if r.started_at else "",
                    "message": (r.error_message or "")[:100],
                }
                for r in runs
            ]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    status = _scheduler_status()
    runs = _recent_runs()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "status": status, "runs": runs, "page": "dashboard"},
    )


@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    try:
        from agent.scheduler.engine import list_jobs

        jobs = list_jobs()
    except Exception:
        jobs = []
    return templates.TemplateResponse(
        "tasks.html",
        {"request": request, "jobs": jobs, "page": "tasks"},
    )


@app.post("/tasks/{job_id}/run")
async def run_task_now(job_id: str):
    from agent.scheduler.engine import run_job_now

    ok = run_job_now(job_id)
    return JSONResponse({"ok": ok})


@app.post("/tasks/{job_id}/delete")
async def delete_task(job_id: str):
    from agent.scheduler.engine import remove_job

    ok = remove_job(job_id)
    return JSONResponse({"ok": ok})


@app.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request):
    from agent.scheduler.registry import list_task_types

    task_types = list_task_types()
    return templates.TemplateResponse(
        "schedule.html",
        {"request": request, "task_types": task_types, "page": "schedule"},
    )


@app.post("/schedule/preview")
async def preview_schedule(expression: str = Form(...)):
    from agent.scheduler.triggers import preview_cron

    try:
        fires = preview_cron(expression, count=5)
        return JSONResponse({"fires": fires})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/credentials", response_class=HTMLResponse)
async def credentials_page(request: Request):
    try:
        from agent.db.session import get_session
        from agent.db.models import CredentialRecord
        from sqlalchemy import select

        with get_session() as session:
            stmt = select(CredentialRecord).order_by(CredentialRecord.name)
            creds = session.execute(stmt).scalars().all()
            cred_list = [
                {
                    "name": c.name,
                    "description": c.description or "",
                    "updated_at": c.updated_at.strftime("%Y-%m-%d") if c.updated_at else "",
                }
                for c in creds
            ]
    except Exception:
        cred_list = []
    return templates.TemplateResponse(
        "credentials.html",
        {"request": request, "credentials": cred_list, "page": "credentials"},
    )


@app.get("/llm", response_class=HTMLResponse)
async def llm_chat_page(request: Request):
    from agent.llm.provider import list_providers

    providers = list_providers()
    return templates.TemplateResponse(
        "llm_chat.html",
        {"request": request, "providers": providers, "page": "llm"},
    )


@app.post("/llm/stream")
async def llm_stream(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    system_prompt = body.get("system_prompt", "You are a helpful assistant.")

    def _generate():
        try:
            from agent.llm.client import LLMClient
            from agent.llm.prompt import PromptBuilder

            client = LLMClient()
            messages = PromptBuilder().system(system_prompt).user(user_message).build()
            for chunk in client.stream(messages):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")


@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "page": "logs"},
    )


@app.get("/api/logs")
async def api_logs():
    """Return last 200 log lines as JSON."""
    try:
        from agent.db.session import get_session
        from agent.db.models import AuditLog, TaskRun
        from sqlalchemy import select

        lines = []
        with get_session() as session:
            stmt = select(TaskRun).order_by(TaskRun.started_at.desc()).limit(50)
            runs = session.execute(stmt).scalars().all()
            for r in runs:
                lines.append(
                    f"[{r.started_at.strftime('%H:%M:%S')}] "
                    f"TASK {r.task_type} ({r.job_id}) → {r.status}"
                )
        return JSONResponse({"lines": lines})
    except Exception:
        return JSONResponse({"lines": []})


@app.get("/api/status")
async def api_status():
    return JSONResponse(_scheduler_status())
