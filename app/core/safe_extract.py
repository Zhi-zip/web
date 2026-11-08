import zipfile
from pathlib import Path


def safe_extract_zip(zip_path, dest_dir):
    """防止 Zip Slip 路径穿越的 zip 解压（跨平台）"""
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            target = (dest_dir / member.filename).resolve()
            # 用 relative_to 判断是否越界，Windows / Linux 都正确
            try:
                target.relative_to(dest_dir)
            except ValueError:
                raise ValueError(f"不安全的路径: {member.filename}")
        zf.extractall(dest_dir)

    return dest_dir