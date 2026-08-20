import re
import tempfile
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Removes invalid Windows characters from the filename."""
    # Strip illegal characters for Windows
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    # Strip trailing spaces or dots
    sanitized = sanitized.strip('. ')
    if not sanitized:
        return "download"
    return sanitized

def get_temp_dir() -> Path:
    """Returns a Path to a temporary directory for OpenTube."""
    base_temp = Path(tempfile.gettempdir()) / "OpenTube"
    base_temp.mkdir(parents=True, exist_ok=True)
    return base_temp
