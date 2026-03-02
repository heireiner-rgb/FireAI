import json
import os
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

from fireai.scenario_loader import DEFAULT_SCENARIO_PATH


def build_temp_scenario_file(tmpdir: str) -> Path:
    scenario_file = Path(tmpdir) / "scenarios.json"
    scenario_file.write_text(DEFAULT_SCENARIO_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return scenario_file


class ApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        scenario_file = build_temp_scenario_file(cls.tempdir.name)
        os.environ["FIREAI_SCENARIO_FILE"] = str(scenario_file)

        from fireai.api import FireAIRequestHandler  # imported after env setup

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FireAIRequestHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.tempdir.cleanup()
        os.environ.pop("FIREAI_SCENARIO_FILE", None)

    def test_root_serves_web_ui(self):
        with urlopen(f"http://127.0.0.1:{self.port}/") as response:
            html = response.read().decode("utf-8")
        self.assertIn("FireAI Bedienoberfläche", html)

    def test_audio_settings_connection_test_endpoint(self):
        req = Request(
            f"http://127.0.0.1:{self.port}/settings/audio-test",
            data=json.dumps(
                {
                    "bluetooth_device_name": "Rescue Headset",
                    "mic_connected": False,
                    "speaker_connected": True,
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req) as response:
            payload = json.loads(response.read().decode("utf-8"))["audio_test"]

        self.assertEqual(payload["overall"], "failed")
        self.assertEqual(payload["microphone"], "failed")
        self.assertEqual(payload["speaker"], "ok")

    def test_create_update_delete_scenario_and_message_flow(self):
        create_scenario_req = Request(
            f"http://127.0.0.1:{self.port}/scenarios",
            data=json.dumps(
                {
                    "name": "Tunnelbrand - verängstigte Person",
                    "injury_level": "mittel",
                    "stress_level": "sehr hoch",
                    "speech_style": "panisch und kurz",
                    "ambient_cues": "Hilfe!, *hustet stark*",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(create_scenario_req) as response:
            created_scenario = json.loads(response.read().decode("utf-8"))["scenario"]

        update_scenario_req = Request(
            f"http://127.0.0.1:{self.port}/scenarios/{created_scenario['scenario_id']}",
            data=json.dumps(
                {
                    "name": "Tunnelbrand - stabile Person",
                    "injury_level": "leicht",
                    "stress_level": "mittel",
                    "speech_style": "ruhiger",
                    "ambient_cues": "Ich glaube es geht, *hustet*",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with urlopen(update_scenario_req) as response:
            updated = json.loads(response.read().decode("utf-8"))["scenario"]
        self.assertEqual(updated["name"], "Tunnelbrand - stabile Person")

        create_session_req = Request(
            f"http://127.0.0.1:{self.port}/sessions",
            data=json.dumps({"scenario_id": created_scenario["scenario_id"]}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(create_session_req) as response:
            created = json.loads(response.read().decode("utf-8"))

        message_req = Request(
            f"http://127.0.0.1:{self.port}/sessions/{created['session_id']}/messages",
            data=json.dumps({"caregiver_text": "Können Sie atmen?"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(message_req) as response:
            message_payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(message_payload["turn_count"], 1)
        self.assertIn("atmen", message_payload["turn"]["patient_response"].lower())

        delete_req = Request(
            f"http://127.0.0.1:{self.port}/scenarios/{created_scenario['scenario_id']}",
            method="DELETE",
        )
        with urlopen(delete_req) as response:
            deleted_payload = json.loads(response.read().decode("utf-8"))
        self.assertEqual(deleted_payload["deleted"], created_scenario["scenario_id"])


if __name__ == "__main__":
    unittest.main()
