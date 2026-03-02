from __future__ import annotations

from dataclasses import asdict
import unicodedata
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from fireai.models import Scenario
from fireai.scenario_loader import load_scenarios, save_scenarios
from fireai.session import FireAISession, SessionTurn


class FireAIService:
    """In-memory application service that manages scenarios and running sessions."""

    def __init__(self, scenario_path: Path | None = None) -> None:
        self._scenario_path = scenario_path
        self._scenarios: List[Scenario] = load_scenarios(path=scenario_path)
        self._sessions: Dict[str, FireAISession] = {}
        self._available_audio_devices = [
            "Rescue Headset A",
            "Rescue Headset B",
            "Integriertes Smartphone Audio",
        ]
        self._audio_settings = {
            "bluetooth_device_name": self._available_audio_devices[0],
            "microphone_device": self._available_audio_devices[0],
            "speaker_device": self._available_audio_devices[0],
        }

    def list_scenarios(self) -> List[dict]:
        return [asdict(scenario) for scenario in self._scenarios]

    def get_audio_settings(self) -> dict:
        return {
            "available_devices": list(self._available_audio_devices),
            "active": dict(self._audio_settings),
        }

    def update_audio_settings(
        self,
        *,
        bluetooth_device_name: str,
        microphone_device: str,
        speaker_device: str,
    ) -> dict:
        for value in [bluetooth_device_name, microphone_device, speaker_device]:
            if value not in self._available_audio_devices:
                raise ValueError(f"Unknown audio device: {value}")

        self._audio_settings = {
            "bluetooth_device_name": bluetooth_device_name,
            "microphone_device": microphone_device,
            "speaker_device": speaker_device,
        }
        return self.get_audio_settings()

    def test_audio_connection(
        self,
        *,
        mic_connected: bool = True,
        speaker_connected: bool = True,
        bluetooth_device_name: str | None = None,
    ) -> dict:
        selected_device = bluetooth_device_name or self._audio_settings["bluetooth_device_name"]
        mic_result = "ok" if mic_connected else "failed"
        speaker_result = "ok" if speaker_connected else "failed"
        overall = "ok" if mic_connected and speaker_connected else "failed"

        details: List[str] = []
        details.append(f"Bluetooth-Gerät: {selected_device}")
        details.append(f"Mikrofon-Gerät: {self._audio_settings['microphone_device']}")
        details.append(f"Speaker-Gerät: {self._audio_settings['speaker_device']}")
        details.append("Mikrofon-Test erfolgreich." if mic_connected else "Mikrofon nicht erreichbar.")
        details.append("Speaker-Test erfolgreich." if speaker_connected else "Speaker nicht erreichbar.")

        return {
            "overall": overall,
            "microphone": mic_result,
            "speaker": speaker_result,
            "details": details,
        }

    def add_scenario(
        self,
        *,
        name: str,
        injury_level: str,
        stress_level: str,
        speech_style: str,
        ambient_cues: List[str],
        scenario_id: str | None = None,
    ) -> dict:
        scenario_id_value = scenario_id or self._slugify(name)
        if any(item.scenario_id == scenario_id_value for item in self._scenarios):
            raise ValueError(f"scenario_id already exists: {scenario_id_value}")

        scenario = self._build_scenario(
            scenario_id=scenario_id_value,
            name=name,
            injury_level=injury_level,
            stress_level=stress_level,
            speech_style=speech_style,
            ambient_cues=ambient_cues,
        )
        self._scenarios.append(scenario)
        self._persist_scenarios()
        return asdict(scenario)

    def update_scenario(
        self,
        scenario_id: str,
        *,
        name: str,
        injury_level: str,
        stress_level: str,
        speech_style: str,
        ambient_cues: List[str],
    ) -> dict:
        index = self._find_scenario_index(scenario_id)
        scenario = self._build_scenario(
            scenario_id=scenario_id,
            name=name,
            injury_level=injury_level,
            stress_level=stress_level,
            speech_style=speech_style,
            ambient_cues=ambient_cues,
        )
        self._scenarios[index] = scenario
        self._persist_scenarios()
        return asdict(scenario)

    def delete_scenario(self, scenario_id: str) -> None:
        index = self._find_scenario_index(scenario_id)
        removed = self._scenarios.pop(index)
        self._persist_scenarios()

        stale_sessions = [sid for sid, sess in self._sessions.items() if sess.state.scenario.scenario_id == removed.scenario_id]
        for session_id in stale_sessions:
            self._sessions.pop(session_id, None)

    def create_session(self, scenario_id: str) -> dict:
        scenario = next((item for item in self._scenarios if item.scenario_id == scenario_id), None)
        if scenario is None:
            raise ValueError(f"Unknown scenario_id: {scenario_id}")

        session_id = str(uuid4())
        self._sessions[session_id] = FireAISession(scenario)

        return {
            "session_id": session_id,
            "scenario": asdict(scenario),
        }

    def post_message(self, session_id: str, caregiver_text: str) -> dict:
        session = self._require_session(session_id)
        turn: SessionTurn = session.process_caregiver_message(caregiver_text)
        return {
            "session_id": session_id,
            "turn": asdict(turn),
            "turn_count": session.state.turn_count,
            "escalation": session.state.escalation,
        }

    def save_session(self, session_id: str, path: str | None = None) -> dict:
        session = self._require_session(session_id)
        target = Path(path) if path else None
        written = session.export_transcript(target)
        return {
            "session_id": session_id,
            "path": str(written),
        }

    def _require_session(self, session_id: str) -> FireAISession:
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Unknown session_id: {session_id}")
        return session

    def _find_scenario_index(self, scenario_id: str) -> int:
        for index, scenario in enumerate(self._scenarios):
            if scenario.scenario_id == scenario_id:
                return index
        raise ValueError(f"Unknown scenario_id: {scenario_id}")

    def _persist_scenarios(self) -> None:
        save_scenarios(self._scenarios, path=self._scenario_path)

    @staticmethod
    def _build_scenario(
        *,
        scenario_id: str,
        name: str,
        injury_level: str,
        stress_level: str,
        speech_style: str,
        ambient_cues: List[str],
    ) -> Scenario:
        cues = [cue.strip() for cue in ambient_cues if cue.strip()]
        if not cues:
            raise ValueError("ambient_cues must contain at least one cue")

        clean_name = name.strip()
        clean_injury = injury_level.strip()
        clean_stress = stress_level.strip()
        clean_speech = speech_style.strip()
        if not clean_name or not clean_injury or not clean_stress or not clean_speech:
            raise ValueError("name, injury_level, stress_level and speech_style are required")

        return Scenario(
            scenario_id=scenario_id,
            name=clean_name,
            injury_level=clean_injury,
            stress_level=clean_stress,
            speech_style=clean_speech,
            ambient_cues=cues,
        )

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        allowed = [c.lower() if c.isalnum() else "_" for c in normalized.strip()]
        slug = "".join(allowed)
        while "__" in slug:
            slug = slug.replace("__", "_")
        return slug.strip("_") or f"scenario_{uuid4().hex[:8]}"
