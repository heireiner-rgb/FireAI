import json
import tempfile
import unittest
from pathlib import Path

from fireai.scenario_loader import DEFAULT_SCENARIO_PATH
from fireai.service import FireAIService


def build_temp_scenario_file(tmpdir: str) -> Path:
    scenario_file = Path(tmpdir) / "scenarios.json"
    scenario_file.write_text(DEFAULT_SCENARIO_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return scenario_file


class ServiceTests(unittest.TestCase):
    def test_create_session_and_message_flow(self):
        service = FireAIService()
        scenarios = service.list_scenarios()

        created = service.create_session(scenarios[0]["scenario_id"])
        session_id = created["session_id"]

        response = service.post_message(session_id, "Können Sie atmen?")

        self.assertEqual(response["session_id"], session_id)
        self.assertEqual(response["turn_count"], 1)
        self.assertIn("atmen", response["turn"]["patient_response"].lower())

    def test_save_session_writes_file(self):
        service = FireAIService()
        session_id = service.create_session(service.list_scenarios()[0]["scenario_id"])["session_id"]
        service.post_message(session_id, "Wo sind Sie?")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "saved.json"
            saved = service.save_session(session_id, str(path))
            self.assertEqual(saved["path"], str(path))

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["turn_count"], 1)
            self.assertEqual(len(payload["history"]), 1)

    def test_audio_settings_update_and_test(self):
        service = FireAIService()
        settings = service.get_audio_settings()
        self.assertGreaterEqual(len(settings["available_devices"]), 1)

        updated = service.update_audio_settings(
            bluetooth_device_name="Rescue Headset B",
            microphone_device="Rescue Headset B",
            speaker_device="Rescue Headset B",
        )
        self.assertEqual(updated["active"]["bluetooth_device_name"], "Rescue Headset B")

        result = service.test_audio_connection(mic_connected=False, speaker_connected=True)
        self.assertEqual(result["overall"], "failed")
        self.assertEqual(result["microphone"], "failed")

    def test_add_update_delete_scenario_persists_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario_file = build_temp_scenario_file(tmpdir)
            service = FireAIService(scenario_path=scenario_file)

            created = service.add_scenario(
                name="Industriebrand - bewusstlose Person",
                injury_level="hoch",
                stress_level="hoch",
                speech_style="schwach und stockend",
                ambient_cues=["Hilfe...", "*hustet*"],
            )
            self.assertIn("industriebrand", created["scenario_id"])

            updated = service.update_scenario(
                created["scenario_id"],
                name="Industriebrand - ansprechbare Person",
                injury_level="mittel",
                stress_level="hoch",
                speech_style="hektisch",
                ambient_cues=["Ich bin hier!", "*keucht*"],
            )
            self.assertEqual(updated["name"], "Industriebrand - ansprechbare Person")

            service.delete_scenario(created["scenario_id"])
            persisted = json.loads(scenario_file.read_text(encoding="utf-8"))
            self.assertFalse(any(item["scenario_id"] == created["scenario_id"] for item in persisted))

    def test_unknown_session_raises(self):
        service = FireAIService()
        with self.assertRaises(ValueError):
            service.post_message("missing", "Hallo?")


if __name__ == "__main__":
    unittest.main()
