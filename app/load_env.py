"""Load `.env` files once (does not override existing environment variables)."""

from __future__ import annotations

import os
from pathlib import Path

_LOADED = False


def _env_file_paths() -> list[Path]:
    app_dir = Path(__file__).resolve().parent
    repo_root = app_dir.parent
    return [repo_root / ".env", app_dir / ".env"]


def load_dotenv_if_present() -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    for path in _env_file_paths():
        if not path.is_file():
            continue
        try:
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip().strip("'").strip('"')
                if key and key not in os.environ:
                    os.environ[key] = val
        except OSError:
            pass
