# FireAI – Kommunikations-App für Feuerwehrübungen

FireAI ist ein lauffähiger Prototyp für eine App, die die Kommunikation mit einer Übungspuppe simuliert.
Der Fokus liegt auf einem **Szenario- und Dialogkern**, der später mit Bluetooth-Audio (Speaker/Mikrofon), STT und TTS verbunden werden kann.

## Release-Status

Der aktuelle Stand ist als **Prototype Release 0.1.0** veröffentlichbar für interne Tests und Demos.

Enthalten:
- CLI-Prototyp für schnelle Szenario-Durchläufe.
- HTTP-API + Web-UI für Bedienung im Browser.
- Szenario-CRUD inkl. Persistierung.
- Audio-Settings (Geräteauswahl) + Mikro/Speaker Verbindungstest.
- Session-Transcript-Export als JSON.

---

## Projektstruktur

- `app.py`: Startpunkt für den CLI-Prototyp.
- `desktop_app.py`: Desktop-GUI (Tkinter) mit Szenarioverwaltung, Session-Chat und Audio-Einstellungen.
- `src/fireai/scenarios.json`: Szenario-Definitionen.
- `src/fireai/models.py`: Datenmodelle (`Scenario`, `SessionState`).
- `src/fireai/dialogue.py`: Antwortlogik und Ambient-Cues.
- `src/fireai/session.py`: Session-Orchestrierung und Transcript-Export.
- `src/fireai/service.py`: In-Memory Service-Layer für Szenarien, Sessions und Audio-Settings.
- `src/fireai/api.py`: HTTP-Server (REST-ähnliche Endpunkte + Web-UI-Auslieferung).
- `src/fireai/web/index.html`: Web-Oberfläche.
- `tests/`: Test-Suite.
- `Makefile`: Standardbefehle (`test`, `run-api`, `run-cli`, `run-gui`).
- `CHANGELOG.md`: Release-Historie.
- `LICENSE`: MIT Lizenz.

---

## Voraussetzungen

- Python 3.10+
- Keine externen Python-Abhängigkeiten im aktuellen Prototyp (nur Standardbibliothek)

Optional:
- `make`

---

## Schnellstart

### API + Web-UI starten

```bash
make run-api
```

oder:

```bash
PYTHONPATH=src python -m fireai.api
```

Dann im Browser öffnen:
- `http://127.0.0.1:8080/`

### CLI starten

```bash
make run-cli
```

oder:

```bash
PYTHONPATH=src python app.py
```

### Desktop-GUI starten

```bash
make run-gui
```

oder:

```bash
PYTHONPATH=src python desktop_app.py
```

Die GUI bietet:
- Szenarien anlegen, bearbeiten, löschen
- Session starten und Nachrichten simulieren
- Audio-Einstellungen wählen und Verbindung testen

---

## API-Endpunkte

- `GET /health`
- `GET /scenarios`
- `POST /scenarios`
- `PUT /scenarios/<scenario_id>`
- `DELETE /scenarios/<scenario_id>`
- `GET /settings/audio`
- `PUT /settings/audio`
- `POST /settings/audio-test`
- `POST /sessions`
- `POST /sessions/<session_id>/messages`
- `POST /sessions/<session_id>/save`

---

## Tests

```bash
make test
```

oder:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

---

## Veröffentlichungs-Checkliste

1. Tests grün ausführen (`make test`).
2. API lokal starten und `/health` prüfen.
3. Optional: Demo-Flow im Browser durchspielen.
4. Tag/Release Notes aus `CHANGELOG.md` übernehmen.
5. Repo nach GitHub pushen:

```bash
git remote add origin <dein-repo-url>
git push -u origin work
```

---

## Nächste technische Schritte

1. Echtes Bluetooth-Audio-Routing im Mobile Client.
2. STT/TTS Integration (lokal oder Cloud).
3. LLM-Dialogmodell statt regelbasierter Antworten.
4. Erweiterte Szenario-Zustandsmaschine (Vitals, Zeitverlauf, Debrief-Metriken).
