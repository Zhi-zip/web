import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import UPLOAD_DIR
from app.tasks.compress_task import compress_task
from app.fastapi_api.schemas import TaskCreated

router = APIRouter(prefix="/api/compress", tags=["compress"])


@router.post("/", response_model=TaskCreated)
async def create_compress(
    files: List[UploadFile] = File(...),
    output_name: str = Form("archive.zip"),
):
    if not files:
        raise HTTPException(400, "没有收到文件")

    # 只允许纯文件名，防止路径穿越
    output_name = Path(output_name).name
    if not output_name.lower().endswith(".zip"):
        output_name += ".zip"

    task_dir = UPLOAD_DIR / uuid.uuid4().hex
    task_dir.mkdir(parents=True)

    mappings, seen = [], set()
    for f in files:
        rel = (f.filename or "unnamed").replace("\\", "/").lstrip("/")
        # 重名加后缀，防覆盖
        base = rel
        i = 1
        while rel in seen:
            p = Path(base)
            rel = f"{p.stem}_{i}{p.suffix}"
            i += 1
        seen.add(rel)

        dest = task_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as fp:
            while chunk := await f.read(1024 * 1024):
                fp.write(chunk)
        mappings.append((str(dest), rel))

    task = compress_task.delay(mappings, output_name)
    return TaskCreated(task_id=task.id, status="PENDING")
