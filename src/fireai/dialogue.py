from __future__ import annotations

from fireai.models import SessionState


def generate_patient_response(state: SessionState, caregiver_text: str) -> str:
    """Simple rule-based stand-in for an AI conversation model."""
    text = caregiver_text.lower()

    if any(token in text for token in ["name", "heißen", "heissen"]):
        return "Ich heiße Alex... bitte bringen Sie mich hier raus!"
    if "atmen" in text:
        return "Es fällt mir schwer zu atmen... ich huste die ganze Zeit."
    if any(token in text for token in ["wo", "ort", "position"]):
        return "Ich bin unten, ich glaube im Keller neben einer Treppe."
    if any(token in text for token in ["verletz", "schmerz", "weh"]):
        return "Mein Bein tut sehr weh, ich kann kaum auftreten."

    if state.escalation >= 2:
        return "Bitte beeilen Sie sich! Ich habe Angst und bekomme schlecht Luft!"

    return "Ja... ich höre Sie. Bitte sagen Sie mir, was ich tun soll."


def next_ambient_cue(state: SessionState) -> str:
    cues = state.scenario.ambient_cues
    if not cues:
        return "*angestrengte Atmung*"
    idx = state.turn_count % len(cues)
    return cues[idx]
