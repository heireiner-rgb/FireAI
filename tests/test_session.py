import json
import tempfile
import unittest
from pathlib import Path

from fireai.scenario_loader import load_scenarios
from fireai.session import FireAISession


class SessionTests(unittest.TestCase):
    def test_load_scenarios_contains_expected_entries(self):
        scenarios = load_scenarios()
        self.assertGreaterEqual(len(scenarios), 3)
        self.assertTrue(scenarios[0].scenario_id)

    def test_session_generates_contextual_response_for_breathing_question(self):
        scenario = load_scenarios()[0]
        session = FireAISession(scenario)

        turn = session.process_caregiver_message("Können Sie atmen?")

        self.assertIn("atmen", turn.patient_response.lower())
        self.assertTrue(turn.ambient_cue)
        self.assertTrue(session.history)

    def test_export_transcript_writes_valid_json(self):
        scenario = load_scenarios()[1]
        session = FireAISession(scenario)
        session.process_caregiver_message("Wo sind Sie?")
        session.process_caregiver_message("Bleiben Sie ruhig.")

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "transcript.json"
            written = session.export_transcript(output)

            self.assertEqual(written, output)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["scenario"]["scenario_id"], scenario.scenario_id)
            self.assertEqual(payload["turn_count"], 2)
            self.assertEqual(len(payload["history"]), 2)


if __name__ == "__main__":
    unittest.main()
