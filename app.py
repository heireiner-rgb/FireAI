from __future__ import annotations

from pathlib import Path

from fireai import FireAISession, load_scenarios


def choose_scenario() -> FireAISession:
    scenarios = load_scenarios()
    print("Verfügbare Szenarien:")
    for i, scenario in enumerate(scenarios, start=1):
        print(f"{i}. {scenario.name} | Verletzung: {scenario.injury_level} | Stress: {scenario.stress_level}")

    while True:
        selection = input("Szenario wählen (Nummer): ").strip()
        if selection.isdigit() and 1 <= int(selection) <= len(scenarios):
            selected = scenarios[int(selection) - 1]
            print(f"\nSzenario gestartet: {selected.name}\n")
            return FireAISession(selected)
        print("Ungültige Auswahl, bitte erneut versuchen.")


def handle_command(session: FireAISession, raw: str) -> str:
    command = raw.strip()
    if command in {"exit", "quit"}:
        print("Session beendet.")
        return "exit"
    if command.startswith("/save"):
        parts = command.split(maxsplit=1)
        path = Path(parts[1]) if len(parts) > 1 else None
        exported = session.export_transcript(path)
        print(f"Transcript gespeichert: {exported}")
        return "handled"
    return "none"


def main() -> None:
    session = choose_scenario()
    print("Tippe 'exit', um die Session zu beenden oder '/save [pfad]' zum Speichern.\n")

    while True:
        caregiver_text = input("Betreuer> ").strip()
        command_state = handle_command(session, caregiver_text)
        if command_state == "exit":
            return
        if command_state == "handled":
            continue
        if not caregiver_text:
            continue

        turn = session.process_caregiver_message(caregiver_text)
        print(f"Puppe (Cue)> {turn.ambient_cue}")
        print(f"Puppe (KI)> {turn.patient_response}\n")


if __name__ == "__main__":
    main()
