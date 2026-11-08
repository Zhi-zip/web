import os
import subprocess
import sys

if __name__ == "__main__":
    os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")
    cmd = [
        sys.executable, "-m", "celery",
        "-A", "app.tasks.celery_app:celery_app",
        "worker",
        "--loglevel=info",
        "--pool=solo",
    ]
    subprocess.run(cmd)
