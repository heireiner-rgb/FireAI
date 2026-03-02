from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from fireai.models import Scenario

DEFAULT_SCENARIO_PATH = Path(__file__).with_name("scenarios.json")


def load_scenarios(path: Path | None = None) -> List[Scenario]:
    target = path or DEFAULT_SCENARIO_PATH
    raw = json.loads(target.read_text(encoding="utf-8"))
    return [Scenario(**item) for item in raw]


def save_scenarios(scenarios: List[Scenario], path: Path | None = None) -> Path:
    target = path or DEFAULT_SCENARIO_PATH
    payload = [asdict(item) for item in scenarios]
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
