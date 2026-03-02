from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from fireai.service import FireAIService

WEB_INDEX_PATH = Path(__file__).with_name("web") / "index.html"


def _build_service() -> FireAIService:
    configured = os.environ.get("FIREAI_SCENARIO_FILE")
    return FireAIService(Path(configured)) if configured else FireAIService()


SERVICE = _build_service()


class FireAIRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            self._write_file(WEB_INDEX_PATH, "text/html; charset=utf-8")
            return
        if self.path == "/health":
            self._write_json(HTTPStatus.OK, {"status": "ok"})
            return
        if self.path == "/scenarios":
            self._write_json(HTTPStatus.OK, {"scenarios": SERVICE.list_scenarios()})
            return
        if self.path == "/settings/audio":
            self._write_json(HTTPStatus.OK, {"audio_settings": SERVICE.get_audio_settings()})
            return
        self._write_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        payload = self._read_json()
        try:
            if self.path == "/scenarios":
                created = SERVICE.add_scenario(**self._scenario_payload(payload, include_id=True))
                self._write_json(HTTPStatus.CREATED, {"scenario": created})
                return

            if self.path == "/settings/audio-test":
                result = SERVICE.test_audio_connection(
                    mic_connected=bool(payload.get("mic_connected", True)),
                    speaker_connected=bool(payload.get("speaker_connected", True)),
                    bluetooth_device_name=payload.get("bluetooth_device_name"),
                )
                self._write_json(HTTPStatus.OK, {"audio_test": result})
                return

            if self.path == "/sessions":
                scenario_id = str(payload.get("scenario_id", ""))
                if not scenario_id:
                    self._write_json(HTTPStatus.BAD_REQUEST, {"error": "scenario_id is required"})
                    return
                self._write_json(HTTPStatus.CREATED, SERVICE.create_session(scenario_id))
                return

            if self.path.startswith("/sessions/") and self.path.endswith("/messages"):
                session_id = self.path[len("/sessions/") : -len("/messages")].strip("/")
                caregiver_text = str(payload.get("caregiver_text", ""))
                if not caregiver_text:
                    self._write_json(HTTPStatus.BAD_REQUEST, {"error": "caregiver_text is required"})
                    return
                self._write_json(HTTPStatus.OK, SERVICE.post_message(session_id, caregiver_text))
                return

            if self.path.startswith("/sessions/") and self.path.endswith("/save"):
                session_id = self.path[len("/sessions/") : -len("/save")].strip("/")
                path = payload.get("path")
                self._write_json(HTTPStatus.OK, SERVICE.save_session(session_id, path))
                return

            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except ValueError as error:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def do_PUT(self) -> None:  # noqa: N802
        payload = self._read_json()
        try:
            if self.path.startswith("/scenarios/"):
                scenario_id = self.path[len("/scenarios/") :].strip("/")
                updated = SERVICE.update_scenario(scenario_id, **self._scenario_payload(payload, include_id=False))
                self._write_json(HTTPStatus.OK, {"scenario": updated})
                return

            if self.path == "/settings/audio":
                settings = SERVICE.update_audio_settings(
                    bluetooth_device_name=str(payload.get("bluetooth_device_name", "")),
                    microphone_device=str(payload.get("microphone_device", "")),
                    speaker_device=str(payload.get("speaker_device", "")),
                )
                self._write_json(HTTPStatus.OK, {"audio_settings": settings})
                return

            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except ValueError as error:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def do_DELETE(self) -> None:  # noqa: N802
        try:
            if self.path.startswith("/scenarios/"):
                scenario_id = self.path[len("/scenarios/") :].strip("/")
                SERVICE.delete_scenario(scenario_id)
                self._write_json(HTTPStatus.OK, {"deleted": scenario_id})
                return
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except ValueError as error:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def _scenario_payload(self, payload: dict[str, Any], *, include_id: bool) -> dict[str, Any]:
        ambient = payload.get("ambient_cues", [])
        if isinstance(ambient, str):
            ambient_cues = [item.strip() for item in ambient.split(",") if item.strip()]
        else:
            ambient_cues = [str(item).strip() for item in ambient if str(item).strip()]

        data = {
            "name": str(payload.get("name", "")),
            "injury_level": str(payload.get("injury_level", "")),
            "stress_level": str(payload.get("stress_level", "")),
            "speech_style": str(payload.get("speech_style", "")),
            "ambient_cues": ambient_cues,
        }
        if include_id:
            data["scenario_id"] = payload.get("scenario_id")
        return data

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _write_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "file not found"})
            return
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), FireAIRequestHandler)
    print(f"FireAI API läuft auf http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
