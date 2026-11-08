from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import OUTPUT_DIR
from app.tasks.celery_app import celery_app

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    r = celery_app.AsyncResult(task_id)
    resp = {"task_id": task_id, "status": r.status}

    if r.status == "PROGRESS":
        info = r.info or {}
        resp["percent"] = info.get("percent", 0)
        resp["current"] = info.get("current")
    elif r.status == "SUCCESS":
        resp["result"] = r.result
    elif r.status == "FAILURE":
        resp["error"] = str(r.info)

    return resp


@router.get("/download/{name}")
async def download(name: str):
    name = Path(name).name
    p = (OUTPUT_DIR / name).resolve()
    root = OUTPUT_DIR.resolve()
    if root not in p.parents and p != root:
        raise HTTPException(404, "Not found")
    if not p.exists() or p.is_dir():
        raise HTTPException(404, "Not found")
    return FileResponse(str(p), filename=p.name)
