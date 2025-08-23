import re
import subprocess
import shutil
from typing import List, Sequence


def slugify(text: str, max_len: int = 80) -> str:
    """Filesystem‑safe slug; ASCII; 0..9, a..z, A..Z, ._-"""
    text = (text or "").strip()
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:max_len] or "item"


def run_cmd(cmd: Sequence[str]) -> subprocess.CompletedProcess:
    """Run command safely (no shell), raise with stderr if non‑zero."""
    if not isinstance(cmd, (list, tuple)) or not all(isinstance(c, str) for c in cmd):
        raise ValueError("cmd must be list/tuple[str]")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"STDERR:\n{proc.stderr.decode('utf-8', errors='replace')}"
        )
    return proc


def which_ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    if not ff:
        raise RuntimeError("FFmpeg not found on PATH")
    return ff
