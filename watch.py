"""Say whether Sillok's daily run is healthy, from its status file alone.

This file is copied into the public repository and run there by a scheduled
workflow, away from the machine it watches. It imports nothing from Sillok.

    python3 watch.py status.json
"""

import json
import sys
from datetime import UTC, datetime, timedelta

QUIET_HOURS = 36
BAD_RUNS = 3


def problems(status: dict, now: datetime) -> list[str]:
    """Return what is wrong: silence for too long, or several bad runs in a row."""
    runs = status.get("runs") or []
    if not runs:
        return ["아직 실행 소식이 한 번도 없음"]
    found = []
    last = datetime.fromisoformat(runs[-1]["at"].replace("Z", "+00:00"))
    quiet = now - last
    if quiet > timedelta(hours=QUIET_HOURS):
        hours = int(quiet.total_seconds() // 3600)
        found.append(
            f"{hours}시간째 소식이 없음(마지막 실행 {last:%Y-%m-%d %H:%M} UTC)"
        )
    recent = runs[-BAD_RUNS:]
    if len(recent) == BAD_RUNS and not any(run["ok"] for run in recent):
        found.append(f"최근 {BAD_RUNS}번의 실행에 모두 문제가 있었음")
    return found


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as handle:
        wrong = problems(json.load(handle), datetime.now(UTC))
    for line in wrong:
        print(f"::error::{line}")
    print("Sillok: 문제 없음" if not wrong else "Sillok: 확인 필요")
    sys.exit(1 if wrong else 0)
