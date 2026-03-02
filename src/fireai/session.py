from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fireai.dialogue import generate_patient_response, next_ambient_cue
from fireai.models import Scenario, SessionState


@dataclass
class SessionTurn:
    caregiver_text: str
    ambient_cue: str
    patient_response: str


class FireAISession:
    """Coordinates scenario state and generated mannequin responses."""

    def __init__(self, scenario: Scenario) -> None:
        self.state = SessionState(scenario=scenario)
        self.history: List[SessionTurn] = []

    def process_caregiver_message(self, caregiver_text: str) -> SessionTurn:
        self.state.advance_turn()
        self.state.escalate_if_needed(caregiver_text)
        ambient_cue = next_ambient_cue(self.state)
        patient_response = generate_patient_response(self.state, caregiver_text)
        turn = SessionTurn(
            caregiver_text=caregiver_text,
            ambient_cue=ambient_cue,
            patient_response=patient_response,
        )
        self.history.append(turn)
        return turn

    def export_transcript(self, output_path: Path | None = None) -> Path:
        if output_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            output_path = Path("exports") / f"session-{self.state.scenario.scenario_id}-{timestamp}.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "scenario": asdict(self.state.scenario),
            "escalation": self.state.escalation,
            "turn_count": self.state.turn_count,
            "history": [asdict(turn) for turn in self.history],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path
