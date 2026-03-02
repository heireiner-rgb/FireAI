# FireAI – Kommunikations-App für Feuerwehrübungen

## Ziel
FireAI ist eine Smartphone-App für realitätsnahe Feuerwehrübungen mit Übungspuppen. 
Die App verbindet eine **Bluetooth Speaker/Mikrofon-Kombination** mit dem Smartphone und ermöglicht:

1. **Szenario-basierte Audio-Simulation** (Schreie, Hilferufe, Husten, Atemnot usw.).
2. **Live-Kommunikation zwischen Betreuer und Übungspuppe** über die Speaker/Mikro-Einheit.
3. **KI-Interaktion**: Wenn der Betreuer spricht, antwortet ein KI-gestützter Charakter passend zum gewählten Szenario.

---

## Kernfunktionen

### 1) Bluetooth-Audio-Anbindung
- Koppeln der Speaker/Mikrofon-Kombi mit dem Smartphone.
- Auswahl des aktiven Audio-Geräts in der App.
- Audio-Routing:
  - Ausgabe der Puppenstimme über den Speaker.
  - Aufnahme der Betreuerstimme über das Mikrofon.

### 2) Szenario-Auswahl
Beispiele:
- **Wohnungsbrand – erwachsene Person**
- **Kellerbrand – orientierungslose Person**
- **Verkehrsunfall – verletzte Person**
- **Kind in Paniksituation**

Pro Szenario konfigurierbar:
- Verletzungsgrad / Bewusstseinslage
- Schmerz- und Stresslevel
- Sprachmuster (kurze Antworten, Panik, Verwirrung)
- Hintergrundgeräusche (Rauch, Husten, Rufen)

### 3) KI-Dialog mit Rollenverhalten
- Speech-to-Text (STT) wandelt die Betreuerrede in Text um.
- Dialog-KI erzeugt rollenkonforme Antwort basierend auf:
  - Szenario
  - Zustand der Übungspuppe
  - Gesprächsverlauf
- Text-to-Speech (TTS) erzeugt die passende Sprachausgabe.

### 4) Simulierte Rufe und Schreie
- Ereignisgesteuerte Audio-Cues (z. B. „Hilfe!“, Hustenanfälle, Schmerzlaute).
- Dynamische Intensität je nach Szenariofortschritt.
- Manuelle Trigger durch den Betreuer als Fallback.

---

## Beispiel-Architektur (MVP)

### Mobile App (Flutter / React Native)
- UI für Szenarioauswahl und Session-Steuerung
- Bluetooth-Handling
- Push-to-Talk / Freisprechmodus
- Latenz- und Audio-Pegelanzeige

### Backend (optional lokal/Cloud)
- Session-Management
- Szenario-Engine
- KI-Orchestrierung (STT → LLM → TTS)
- Logging für Nachbesprechung

### KI-Komponenten
- **STT**: z. B. Whisper oder Cloud-STT
- **LLM**: Rollenprompt + Sicherheitsregeln
- **TTS**: emotionsfähige Stimme (ruhig/panisch/schwach)

---

## Beispiel-Dialogfluss
1. Betreuer startet Szenario „Kellerbrand“.
2. App spielt initiale Rufe der Übungspuppe ab.
3. Betreuer fragt: „Können Sie mich hören? Wo sind Sie verletzt?“
4. STT transkribiert die Frage.
5. KI generiert situative Antwort: „Ich... ich glaube mein Bein ist eingeklemmt... ich bekomme schlecht Luft...“
6. TTS gibt die Antwort über den Bluetooth-Speaker aus.
7. Szenario eskaliert oder beruhigt sich je nach Kommunikationsqualität.

---

## Sicherheits- und Qualitätsanforderungen
- Kein medizinischer Rat als Fakt, sondern simulationsgerechte Rollenantworten.
- Moderationsfilter gegen unpassende Inhalte.
- Offline-Fallback mit vordefinierten Phrasen bei Netzwerkausfall.
- DSGVO-konforme Verarbeitung, möglichst ohne dauerhafte Speicherung personenbezogener Daten.

---

## MVP-Roadmap

### Phase 1
- Bluetooth-Audio-Verbindung stabilisieren
- 2–3 feste Szenarien
- Vorgefertigte Audio-Cues + einfache KI-Antworten

### Phase 2
- Dynamische Zustandsmaschine im Szenario
- Verbesserte TTS-Stimmen (Emotionen)
- Debrief-Ansicht mit Kommunikationsverlauf

### Phase 3
- Mehrsprachigkeit
- Multi-Rollen-Übungen (mehrere Verletzte)
- Bewertungssystem für Ausbildungserfolg

---

## Nächste Umsetzungsschritte
1. Technologie-Entscheidung für Mobile-Stack (Flutter oder React Native).
2. Auswahl von STT/TTS/LLM-Anbietern nach Latenz und Offline-Fähigkeit.
3. Definition eines Szenario-Datenmodells (JSON-basiert).
4. Prototyp mit einem End-to-End-Szenario und realer Bluetooth-Hardware.

