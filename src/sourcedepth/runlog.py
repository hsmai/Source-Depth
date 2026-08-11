"""단계 시각 로깅 + BLOCKED 프로토콜 + 환경 기록 (브리프 C-5·PART F)."""
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from .config import LOGS_DIR

BLOCKED_EXIT = 86


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


_tail_checked: set = set()


def append_jsonl(path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    # 강제 종료로 잘린 마지막 행 뒤에 이어 붙으면 두 레코드가 무음 소실됨 —
    # 프로세스당 1회, 파일 끝이 개행인지 확인하고 아니면 종결시킨다 (read_jsonl이 잘린 행 폐기)
    if str(path) not in _tail_checked:
        _tail_checked.add(str(path))
        if path.exists() and path.stat().st_size > 0:
            with open(path, "rb") as f:
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    with open(path, "ab") as g:
                        g.write(b"\n")
    with open(path, "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # 강제 종료로 잘린 마지막 행 허용 (resume가 재계산)
    return rows


def _stage_event(stage: str, event: str, extra: dict | None = None):
    row = {"stage": stage, "event": event, "ts": iso_now(),
           "host": os.uname().nodename, "pbs_job_id": os.environ.get("PBS_JOBID", "")}
    if extra:
        row.update(extra)
    append_jsonl(LOGS_DIR / "stage_times.jsonl", row)


@contextmanager
def stage(name: str):
    _stage_event(name, "start")
    t0 = time.time()
    try:
        yield
    except SystemExit:
        raise
    except Exception as e:
        _stage_event(name, "error", {"error": repr(e), "elapsed_s": round(time.time() - t0)})
        raise
    _stage_event(name, "end", {"elapsed_s": round(time.time() - t0)})


def blocked(stage_name: str, reason: str, detail: dict | None = None):
    """대안 실행 금지 — 기록 후 즉시 종료 (브리프 헤더 원칙)."""
    entry = (f"\n## BLOCKED {iso_now()}\n- stage: {stage_name}\n- reason: {reason}\n"
             f"- detail: {json.dumps(detail or {}, ensure_ascii=False, default=str)}\n"
             f"- host: {os.uname().nodename} / job: {os.environ.get('PBS_JOBID', '-')}\n")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOGS_DIR / "BLOCKED.md", "a") as f:
        f.write(entry)
    _stage_event(stage_name, "BLOCKED", {"reason": reason})
    print(f"[BLOCKED] {stage_name}: {reason}", file=sys.stderr)
    sys.exit(BLOCKED_EXIT)


def dump_env(stage_name: str):
    info = {"stage": stage_name, "ts": iso_now(), "argv": sys.argv,
            "python": sys.version.split()[0]}
    for mod in ("torch", "transformers", "numpy", "pandas", "statsmodels", "PIL", "scipy"):
        try:
            m = __import__(mod)
            info[mod] = getattr(m, "__version__", "?")
        except ImportError:
            info[mod] = None
    try:
        info["nvidia_smi"] = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:
        info["nvidia_smi"] = f"unavailable: {e}"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOGS_DIR / f"env_{stage_name}.json", "w") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    return info
