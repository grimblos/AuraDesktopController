"""
Aura GUI Dashboard
CustomTkinter interface for configuration and monitoring.
"""

import customtkinter as ctk
from PIL import Image
import os

class AuraApp(ctk.CTk):
    def __init__(self, event_queue=None, control_queue=None):
        """
        Initialize the main GUI window and layout.
        """
        super().__init__()
        self.event_queue = event_queue
        self.control_queue = control_queue
        
        self.title("Aura: Distributed Voice & Gesture Controller")
        self.geometry("1000x650")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._setup_ui()

    def _setup_ui(self):
        """
        Create and arrange UI components.
        """
        # Create Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="AURA", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=20)

        # Tab Buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self._show_tab("dashboard"))
        self.btn_dashboard.pack(pady=10, padx=20)

        self.btn_settings = ctk.CTkButton(self.sidebar, text="Settings", command=lambda: self._show_tab("settings"))
        self.btn_settings.pack(pady=10, padx=20)

        # --- Content Area ---
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="right", fill="both", expand=True)

        # --- Dashboard Frame ---
        self.dashboard_frame = ctk.CTkFrame(self.container)
        
        self.dash_label = ctk.CTkLabel(self.dashboard_frame, text="System Log", font=ctk.CTkFont(size=20, weight="bold"))
        self.dash_label.pack(pady=10)
        
        self.log_view = ctk.CTkTextbox(self.dashboard_frame, height=400)
        self.log_view.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Settings Frame ---
        self.settings_frame = ctk.CTkFrame(self.container)
        
        self.settings_label = ctk.CTkLabel(self.settings_frame, text="System Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.settings_label.pack(pady=20)

        # Wake Word Setting
        self.wake_word_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.wake_word_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(self.wake_word_frame, text="Wake Word:").pack(side="left")
        self.wake_word_entry = ctk.CTkEntry(self.wake_word_frame, width=150)
        self.wake_word_entry.insert(0, "computer")  # Default
        self.wake_word_entry.pack(side="left", padx=10)
        
        self.btn_set_wake = ctk.CTkButton(self.wake_word_frame, text="Apply", width=60, command=self._set_wake_word)
        self.btn_set_wake.pack(side="left")

        # Engine Toggles
        self.gesture_var = ctk.BooleanVar(value=True)
        self.gesture_check = ctk.CTkSwitch(self.settings_frame, text="Gesture Engine Active", 
                                            variable=self.gesture_var, command=self._toggle_gesture)
        self.gesture_check.pack(pady=10, padx=20, anchor="w")

        self.voice_var = ctk.BooleanVar(value=True)
        self.voice_check = ctk.CTkSwitch(self.settings_frame, text="Voice Engine Active", 
                                            variable=self.voice_var, command=self._toggle_voice)
        self.voice_check.pack(pady=10, padx=20, anchor="w")

        # Preview Toggle
        self.preview_var = ctk.BooleanVar(value=False)
        self.preview_check = ctk.CTkSwitch(self.settings_frame, text="Show Camera Preview", 
                                            variable=self.preview_var, command=self._toggle_preview)
        self.preview_check.pack(pady=10, padx=20, anchor="w")

        self._show_tab("dashboard")

    def _show_tab(self, tab_name):
        """Switch visible frames."""
        if tab_name == "dashboard":
            self.dashboard_frame.pack(fill="both", expand=True)
            self.settings_frame.pack_forget()
        elif tab_name == "settings":
            self.dashboard_frame.pack_forget()
            self.settings_frame.pack(fill="both", expand=True)

    def _toggle_preview(self):
        enabled = self.preview_var.get()
        if self.control_queue:
            self.control_queue.put({"target": "gesture", "action": "toggle_preview", "value": enabled})
        self.update_log(f"Camera Preview: {'Enabled' if enabled else 'Disabled'}")

    def _set_wake_word(self):
        new_word = self.wake_word_entry.get().strip()
        if new_word and self.control_queue:
            self.control_queue.put({"target": "voice", "action": "set_wake_word", "value": new_word})
            self.update_log(f"Wake word updated to: '{new_word}'")
            
    def _toggle_gesture(self):
        enabled = self.gesture_var.get()
        action = "start" if enabled else "stop"
        if self.control_queue:
            self.control_queue.put({"target": "gesture", "action": action})
        self.update_log(f"Gesture Engine {'Resumed' if enabled else 'Paused'}")

    def _toggle_voice(self):
        enabled = self.voice_var.get()
        action = "start" if enabled else "stop"
        if self.control_queue:
            self.control_queue.put({"target": "voice", "action": action})
        self.update_log(f"Voice Engine {'Resumed' if enabled else 'Paused'}")

    def update_log(self, message):
        """Append a message to the dashboard log view."""
        if hasattr(self, 'log_view'):
            self.log_view.insert("end", f"> {message}\n")
            self.log_view.see("end")

    def run(self):
        self.mainloop()
