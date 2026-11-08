import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import UPLOAD_DIR
from app.tasks.decompress_task import decompress_task
from app.fastapi_api.schemas import TaskCreated

router = APIRouter(prefix="/api/decompress", tags=["decompress"])


@router.post("/", response_model=TaskCreated)
async def create_decompress(file: UploadFile = File(...)):
    name = Path(file.filename or "archive.zip").name
    if not name.lower().endswith(".zip"):
        raise HTTPException(400, "目前仅支持 .zip")

    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}_{name}"
    with open(dest, "wb") as fp:
        while chunk := await file.read(1024 * 1024):
            fp.write(chunk)

    task = decompress_task.delay(str(dest), name.rsplit(".", 1)[0])
    return TaskCreated(task_id=task.id, status="PENDING")
