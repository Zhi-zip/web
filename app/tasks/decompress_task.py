from app.tasks.celery_app import celery_app
from app.core.safe_extract import safe_extract_zip
from app.config import OUTPUT_DIR


@celery_app.task(bind=True)
def decompress_task(self, zip_path, name):
    dest = OUTPUT_DIR / f"{name}_extracted"
    safe_extract_zip(zip_path, dest)
    return {"name": dest.name, "output": str(dest)}
