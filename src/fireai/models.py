from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Scenario:
    """Training scenario configuration used by the simulation engine."""

    scenario_id: str
    name: str
    injury_level: str
    stress_level: str
    speech_style: str
    ambient_cues: List[str] = field(default_factory=list)


@dataclass
class SessionState:
    """Runtime state of a running mannequin communication session."""

    scenario: Scenario
    escalation: int = 0
    turn_count: int = 0

    def advance_turn(self) -> None:
        self.turn_count += 1

    def escalate_if_needed(self, caregiver_text: str) -> None:
        lowered = caregiver_text.lower()
        if any(token in lowered for token in ["wo", "atmen", "verletz", "ruhe", "hör", "hoer"]):
            self.escalation = max(0, self.escalation - 1)
        else:
            self.escalation = min(3, self.escalation + 1)
