from app.tasks.celery_app import celery_app
from app.core.archiver import zip_files
from app.config import OUTPUT_DIR


@celery_app.task(bind=True)
def compress_task(self, file_mappings, output_name):
    def cb(processed, total, current):
        self.update_state(
            state="PROGRESS",
            meta={"percent": int(processed / total * 100), "current": current},
        )

    out = OUTPUT_DIR / output_name
    zip_files(file_mappings, out, cb)
    return {"name": output_name, "output": str(out)}
