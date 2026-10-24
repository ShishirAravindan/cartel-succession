"""Run-directory writer for the logging contract (CLAUDE.md).

runs/<run_id>/
  config.json          run settings, written once at start
  calls.jsonl          one line per LLM call attempt (incl. retries and transport errors)
  rounds.jsonl         one line per completed round (market state)
  snapshot_T<t>.json   full state (history + notes per seat) at branch points
  status.json          how the run ended

Field notes beyond the names in CLAUDE.md:
  rendered_prompt        exact string the model received, or null on chat endpoints
  rendered_prompt_local  our Qwen3 chat-template rendering (always present)
  messages               the chat messages sent / rendered
  notes_text             {"plans", "insights"} this call wrote, or null if the parse failed

Always run as `python -m seat_swap.<module>`: this file is named logging.py and would
shadow the stdlib module if seat_swap/ itself were on sys.path.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

CALL_FIELDS = (
    "run_id", "phase", "arm", "seed", "round", "seat", "model", "model_revision", "provider",
    "rendered_prompt", "sampling_params", "raw_completion", "parsed_price", "parse_ok",
    "notes_text", "timestamp",
)
ROUND_FIELDS = (
    "run_id", "phase", "arm", "seed", "round", "prices", "quantities", "profits", "shock",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class RunLogger:
    def __init__(self, runs_root: str | Path, run_id: str):
        self.run_id = run_id
        self.dir = Path(runs_root) / run_id
        self.dir.parent.mkdir(parents=True, exist_ok=True)
        self.dir.mkdir(exist_ok=False)  # never overwrite a run directory
        self._lock = threading.Lock()

    def _append(self, name: str, record: dict) -> None:
        line = json.dumps(record, ensure_ascii=False)
        with self._lock, open(self.dir / name, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _write_json(self, name: str, obj: dict) -> None:
        with self._lock, open(self.dir / name, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)

    def config(self, cfg: dict) -> None:
        if (self.dir / "config.json").exists():
            raise FileExistsError(self.dir / "config.json")
        self._write_json("config.json", cfg)

    def call(self, record: dict) -> None:
        missing = [k for k in CALL_FIELDS if k not in record]
        if missing:
            raise KeyError(f"call record missing {missing}")
        self._append("calls.jsonl", {**record, "timestamp": record["timestamp"] or now()})

    def round(self, record: dict) -> None:
        missing = [k for k in ROUND_FIELDS if k not in record]
        if missing:
            raise KeyError(f"round record missing {missing}")
        self._append("rounds.jsonl", {**record, "timestamp": now()})

    def snapshot(self, t: int, state: dict) -> Path:
        path = self.dir / f"snapshot_T{t}.json"
        if path.exists():
            raise FileExistsError(path)
        self._write_json(path.name, state)
        return path

    def status(self, status: dict) -> None:
        self._write_json("status.json", {**status, "timestamp": now()})
