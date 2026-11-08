import zipfile
from pathlib import Path


def zip_files(file_mappings, output_path, progress_callback=None):
    """
    file_mappings: [(source_path_str, arcname_str), ...]
    保持相对目录结构，arcname 作为 zip 内部条目名，天然防覆盖。
    """
    total = max(len(file_mappings), 1)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, (src, arc) in enumerate(file_mappings, 1):
            zf.write(src, arc)
            if progress_callback:
                progress_callback(i, total, arc)

    return output_path
