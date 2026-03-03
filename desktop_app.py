from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from fireai import FireAIService


class FireAIGuiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("FireAI Desktop GUI")
        self.root.geometry("980x720")

        self.service = FireAIService()
        self.session_id: str | None = None
        self.scenario_id_map: dict[str, str] = {}

        self._build_ui()
        self.refresh_scenarios()
        self.refresh_audio_settings()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.scenario_tab = ttk.Frame(notebook)
        self.session_tab = ttk.Frame(notebook)
        self.settings_tab = ttk.Frame(notebook)

        notebook.add(self.scenario_tab, text="Szenarien")
        notebook.add(self.session_tab, text="Session")
        notebook.add(self.settings_tab, text="Audio-Einstellungen")

        self._build_scenario_tab()
        self._build_session_tab()
        self._build_settings_tab()

    def _build_scenario_tab(self) -> None:
        frame = ttk.Frame(self.scenario_tab, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Name").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=45).grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(frame, text="Verletzungsgrad").grid(row=1, column=0, sticky="w")
        self.injury_var = tk.StringVar(value="mittel")
        ttk.Entry(frame, textvariable=self.injury_var, width=45).grid(row=1, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(frame, text="Stresslevel").grid(row=2, column=0, sticky="w")
        self.stress_var = tk.StringVar(value="hoch")
        ttk.Entry(frame, textvariable=self.stress_var, width=45).grid(row=2, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(frame, text="Sprachstil").grid(row=3, column=0, sticky="w")
        self.speech_var = tk.StringVar(value="panisch")
        ttk.Entry(frame, textvariable=self.speech_var, width=45).grid(row=3, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(frame, text="Ambient-Cues (Komma getrennt)").grid(row=4, column=0, sticky="w")
        self.cues_var = tk.StringVar(value="Hilfe!, *hustet*")
        ttk.Entry(frame, textvariable=self.cues_var, width=45).grid(row=4, column=1, sticky="ew", padx=6, pady=4)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=1, sticky="w", pady=8)
        ttk.Button(button_frame, text="Neu speichern", command=self.create_scenario).pack(side="left", padx=3)
        ttk.Button(button_frame, text="Auswahl laden", command=self.load_selected_scenario).pack(side="left", padx=3)
        ttk.Button(button_frame, text="Aktualisieren", command=self.update_scenario).pack(side="left", padx=3)
        ttk.Button(button_frame, text="Löschen", command=self.delete_scenario).pack(side="left", padx=3)

        ttk.Label(frame, text="Vorhandene Szenarien").grid(row=6, column=0, sticky="nw", pady=(10, 4))
        self.scenario_list = tk.Listbox(frame, height=12)
        self.scenario_list.grid(row=6, column=1, sticky="nsew", padx=6, pady=(10, 4))

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(6, weight=1)

    def _build_session_tab(self) -> None:
        frame = ttk.Frame(self.session_tab, padding=10)
        frame.pack(fill="both", expand=True)

        row = ttk.Frame(frame)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Szenario").pack(side="left")
        self.session_scenario_var = tk.StringVar()
        self.session_scenario_combo = ttk.Combobox(row, textvariable=self.session_scenario_var, state="readonly", width=65)
        self.session_scenario_combo.pack(side="left", padx=6)
        ttk.Button(row, text="Session starten", command=self.start_session).pack(side="left")

        self.session_status = tk.StringVar(value="Keine aktive Session")
        ttk.Label(frame, textvariable=self.session_status).pack(anchor="w", pady=(0, 8))

        input_row = ttk.Frame(frame)
        input_row.pack(fill="x", pady=4)
        self.message_var = tk.StringVar()
        ttk.Entry(input_row, textvariable=self.message_var).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(input_row, text="Senden", command=self.send_message).pack(side="left")

        self.log = tk.Text(frame, height=22)
        self.log.pack(fill="both", expand=True, pady=6)

    def _build_settings_tab(self) -> None:
        frame = ttk.Frame(self.settings_tab, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Bluetooth-Gerät").grid(row=0, column=0, sticky="w")
        self.bt_var = tk.StringVar()
        self.bt_combo = ttk.Combobox(frame, textvariable=self.bt_var, state="readonly", width=45)
        self.bt_combo.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(frame, text="Mikrofon").grid(row=1, column=0, sticky="w")
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(frame, textvariable=self.mic_var, state="readonly", width=45)
        self.mic_combo.grid(row=1, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(frame, text="Speaker").grid(row=2, column=0, sticky="w")
        self.speaker_var = tk.StringVar()
        self.speaker_combo = ttk.Combobox(frame, textvariable=self.speaker_var, state="readonly", width=45)
        self.speaker_combo.grid(row=2, column=1, sticky="ew", padx=6, pady=4)

        self.mic_connected = tk.BooleanVar(value=True)
        self.speaker_connected = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Mikrofon verbunden", variable=self.mic_connected).grid(row=3, column=1, sticky="w", pady=4)
        ttk.Checkbutton(frame, text="Speaker verbunden", variable=self.speaker_connected).grid(row=4, column=1, sticky="w", pady=4)

        action_row = ttk.Frame(frame)
        action_row.grid(row=5, column=1, sticky="w", pady=8)
        ttk.Button(action_row, text="Einstellungen speichern", command=self.save_audio_settings).pack(side="left", padx=3)
        ttk.Button(action_row, text="Verbindung testen", command=self.test_audio).pack(side="left", padx=3)

        self.audio_info = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.audio_info, wraplength=700).grid(row=6, column=0, columnspan=2, sticky="w")

        frame.columnconfigure(1, weight=1)

    def _selected_scenario_id(self) -> str | None:
        sel = self.scenario_list.curselection()
        if not sel:
            return None
        line = self.scenario_list.get(sel[0])
        return self.scenario_id_map.get(line)

    def _scenario_payload(self) -> dict:
        cues = [item.strip() for item in self.cues_var.get().split(",") if item.strip()]
        return {
            "name": self.name_var.get(),
            "injury_level": self.injury_var.get(),
            "stress_level": self.stress_var.get(),
            "speech_style": self.speech_var.get(),
            "ambient_cues": cues,
        }

    def refresh_scenarios(self) -> None:
        scenarios = self.service.list_scenarios()
        self.scenario_id_map.clear()
        self.scenario_list.delete(0, tk.END)

        labels = []
        for scenario in scenarios:
            label = f"{scenario['name']} [{scenario['scenario_id']}]"
            labels.append(label)
            self.scenario_id_map[label] = scenario["scenario_id"]
            self.scenario_list.insert(tk.END, label)

        self.session_scenario_combo["values"] = labels
        if labels and not self.session_scenario_var.get():
            self.session_scenario_var.set(labels[0])

    def create_scenario(self) -> None:
        try:
            self.service.add_scenario(**self._scenario_payload())
            self.refresh_scenarios()
            messagebox.showinfo("OK", "Szenario erstellt")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Fehler", str(exc))

    def load_selected_scenario(self) -> None:
        scenario_id = self._selected_scenario_id()
        if not scenario_id:
            messagebox.showwarning("Hinweis", "Bitte ein Szenario auswählen")
            return

        selected = next((s for s in self.service.list_scenarios() if s["scenario_id"] == scenario_id), None)
        if not selected:
            return
        self.name_var.set(selected["name"])
        self.injury_var.set(selected["injury_level"])
        self.stress_var.set(selected["stress_level"])
        self.speech_var.set(selected["speech_style"])
        self.cues_var.set(", ".join(selected["ambient_cues"]))

    def update_scenario(self) -> None:
        scenario_id = self._selected_scenario_id()
        if not scenario_id:
            messagebox.showwarning("Hinweis", "Bitte ein Szenario auswählen")
            return
        try:
            self.service.update_scenario(scenario_id, **self._scenario_payload())
            self.refresh_scenarios()
            messagebox.showinfo("OK", "Szenario aktualisiert")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Fehler", str(exc))

    def delete_scenario(self) -> None:
        scenario_id = self._selected_scenario_id()
        if not scenario_id:
            messagebox.showwarning("Hinweis", "Bitte ein Szenario auswählen")
            return
        try:
            self.service.delete_scenario(scenario_id)
            self.refresh_scenarios()
            messagebox.showinfo("OK", "Szenario gelöscht")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Fehler", str(exc))

    def start_session(self) -> None:
        label = self.session_scenario_var.get()
        scenario_id = self.scenario_id_map.get(label)
        if not scenario_id:
            messagebox.showwarning("Hinweis", "Bitte ein Szenario auswählen")
            return

        try:
            created = self.service.create_session(scenario_id)
            self.session_id = created["session_id"]
            self.session_status.set(f"Aktive Session: {self.session_id}")
            self.log.delete("1.0", tk.END)
            self.log.insert(tk.END, f"Session gestartet: {created['scenario']['name']}\n\n")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Fehler", str(exc))

    def send_message(self) -> None:
        if not self.session_id:
            messagebox.showwarning("Hinweis", "Bitte zuerst eine Session starten")
            return
        text = self.message_var.get().strip()
        if not text:
            return
        try:
            response = self.service.post_message(self.session_id, text)
            turn = response["turn"]
            self.log.insert(tk.END, f"Betreuer: {text}\n")
            self.log.insert(tk.END, f"Puppe Cue: {turn['ambient_cue']}\n")
            self.log.insert(tk.END, f"Puppe KI: {turn['patient_response']}\n---\n")
            self.log.see(tk.END)
            self.message_var.set("")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Fehler", str(exc))

    def refresh_audio_settings(self) -> None:
        settings = self.service.get_audio_settings()
        devices = settings["available_devices"]
        self.bt_combo["values"] = devices
        self.mic_combo["values"] = devices
        self.speaker_combo["values"] = devices

        active = settings["active"]
        self.bt_var.set(active["bluetooth_device_name"])
        self.mic_var.set(active["microphone_device"])
        self.speaker_var.set(active["speaker_device"])

    def save_audio_settings(self) -> None:
        try:
            settings = self.service.update_audio_settings(
                bluetooth_device_name=self.bt_var.get(),
                microphone_device=self.mic_var.get(),
                speaker_device=self.speaker_var.get(),
            )
            active = settings["active"]
            self.audio_info.set(
                f"Gespeichert: BT={active['bluetooth_device_name']} | Mic={active['microphone_device']} | Speaker={active['speaker_device']}"
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Fehler", str(exc))

    def test_audio(self) -> None:
        result = self.service.test_audio_connection(
            mic_connected=self.mic_connected.get(),
            speaker_connected=self.speaker_connected.get(),
            bluetooth_device_name=self.bt_var.get(),
        )
        self.audio_info.set(f"Audio-Test: {result['overall']} | {' '.join(result['details'])}")


def main() -> None:
    root = tk.Tk()
    FireAIGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
