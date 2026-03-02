from __future__ import annotations

import json
from pathlib import Path
from typing import List

from fireai.models import Scenario


def load_scenarios(path: Path | None = None) -> List[Scenario]:
    if path is None:
        path = Path(__file__).with_name("scenarios.json")

    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Scenario(**item) for item in raw]
