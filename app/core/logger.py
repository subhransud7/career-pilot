from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class DailyLogger:
    def __init__(self, root: str = "logs"):
        self.root = Path(root)

    def _folder(self) -> Path:
        day = datetime.now().strftime("%d-%m-%Y")
        folder = self.root / f"logs-{day}"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def _append(self, filename: str, line: str) -> None:
        file_path = self._folder() / filename
        timestamp = datetime.now().isoformat(timespec="seconds")
        with file_path.open("a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {line}\n")

    def run(self, message: str) -> None:
        self._append("run.log", message)

    def llm(self, payload: dict) -> None:
        self._append("llm_calls.log", json.dumps(payload, ensure_ascii=True))

    def error(self, message: str) -> None:
        self._append("errors.log", message)
