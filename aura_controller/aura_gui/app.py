"""
Aura GUI Dashboard
CustomTkinter interface for configuration and monitoring.
"""

import customtkinter as ctk
from PIL import Image
import os

class AuraApp(ctk.CTk):
    def __init__(self, event_queue=None, control_queue=None, cfg_manager=None):
        """
        Initialize the main GUI window and layout.
        """
        super().__init__()
        self.event_queue = event_queue
        self.control_queue = control_queue
        self.cfg_manager = cfg_manager
        
        self.hotkey_rows = []
        self.ahk_rows = []
        self.internal_rows = []
        self.trigger_rows = []
        
        self.title("Aura: Distributed Voice & Gesture Controller")
        self.geometry("1100x700")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._setup_ui()

    def _setup_ui(self):
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

        self.btn_macros = ctk.CTkButton(self.sidebar, text="Macros", command=lambda: self._show_tab("macros"))
        self.btn_macros.pack(pady=10, padx=20)
        
        self.btn_gestures = ctk.CTkButton(self.sidebar, text="Gestures", command=lambda: self._show_tab("gestures"))
        self.btn_gestures.pack(pady=10, padx=20)
        
        self.btn_triggers = ctk.CTkButton(self.sidebar, text="Triggers", command=lambda: self._show_tab("triggers"))
        self.btn_triggers.pack(pady=10, padx=20)

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

        self.wake_word_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.wake_word_frame.pack(fill="x", pady=10, padx=20)
        ctk.CTkLabel(self.wake_word_frame, text="Wake Word:").pack(side="left")
        self.wake_word_entry = ctk.CTkEntry(self.wake_word_frame, width=150)
        self.wake_word_entry.insert(0, self.cfg_manager.config["engines"]["voice"].get("wake_word", "computer") if self.cfg_manager else "computer")
        self.wake_word_entry.pack(side="left", padx=10)
        self.btn_set_wake = ctk.CTkButton(self.wake_word_frame, text="Apply", width=60, command=self._set_wake_word)
        self.btn_set_wake.pack(side="left")

        gesture_enabled = self.cfg_manager.config["engines"]["gesture"].get("enabled", True) if self.cfg_manager else True
        self.gesture_var = ctk.BooleanVar(value=gesture_enabled)
        self.gesture_check = ctk.CTkSwitch(self.settings_frame, text="Gesture Engine Active", variable=self.gesture_var, command=self._toggle_gesture)
        self.gesture_check.pack(pady=10, padx=20, anchor="w")

        voice_enabled = self.cfg_manager.config["engines"]["voice"].get("enabled", True) if self.cfg_manager else True
        self.voice_var = ctk.BooleanVar(value=voice_enabled)
        self.voice_check = ctk.CTkSwitch(self.settings_frame, text="Voice Engine Active", variable=self.voice_var, command=self._toggle_voice)
        self.voice_check.pack(pady=10, padx=20, anchor="w")

        # --- Macros Frame ---
        self.macros_frame = ctk.CTkFrame(self.container)
        self.macros_label = ctk.CTkLabel(self.macros_frame, text="Macro Definitions", font=ctk.CTkFont(size=20, weight="bold"))
        self.macros_label.pack(pady=10)
        
        self.macros_tabs = ctk.CTkTabview(self.macros_frame, width=700, height=450)
        self.macros_tabs.pack(pady=10, padx=20, fill="both", expand=True)
        self.macros_tabs.add("Hotkeys")
        self.macros_tabs.add("AHK Scripts")
        self.macros_tabs.add("Built-in")
        
        self.hotkeys_scroll = ctk.CTkScrollableFrame(self.macros_tabs.tab("Hotkeys"))
        self.hotkeys_scroll.pack(fill="both", expand=True)
        self.btn_add_hotkey = ctk.CTkButton(self.macros_tabs.tab("Hotkeys"), text="+ Add Hotkey", command=self._add_empty_hotkey)
        self.btn_add_hotkey.pack(pady=10, side="left")
        
        self.ahk_scroll = ctk.CTkScrollableFrame(self.macros_tabs.tab("AHK Scripts"))
        self.ahk_scroll.pack(fill="both", expand=True)
        self.btn_add_ahk = ctk.CTkButton(self.macros_tabs.tab("AHK Scripts"), text="+ Add Script", command=self._add_empty_ahk)
        self.btn_add_ahk.pack(pady=10, side="left")
        
        self.internal_scroll = ctk.CTkScrollableFrame(self.macros_tabs.tab("Built-in"))
        self.internal_scroll.pack(fill="both", expand=True)
        ctk.CTkLabel(self.internal_scroll, text="Built-in macros cannot be edited or deleted.", text_color="gray").pack(pady=10)

        self.btn_save_macros = ctk.CTkButton(self.macros_frame, text="Save Config", command=self._save_config, fg_color="green")
        self.btn_save_macros.pack(pady=10, padx=20, side="right")

        # --- Gestures Frame ---
        self.gestures_frame = ctk.CTkFrame(self.container)
        self.gestures_label = ctk.CTkLabel(self.gestures_frame, text="Gesture Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.gestures_label.pack(pady=10)
        
        # Left side: Gesture list. Right side: Placeholder for preview
        self.gestures_split = ctk.CTkFrame(self.gestures_frame, fg_color="transparent")
        self.gestures_split.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.gestures_list_frame = ctk.CTkScrollableFrame(self.gestures_split, width=300)
        self.gestures_list_frame.pack(side="left", fill="y", expand=False, padx=(0, 10))
        
        self.gestures_preview_frame = ctk.CTkFrame(self.gestures_split, width=400)
        self.gestures_preview_frame.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(self.gestures_preview_frame, text="Gesture Camera Preview", font=ctk.CTkFont(weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.gestures_preview_frame, text="(Phase 2 Feature: Embedded Camera Feed)", text_color="gray").pack()
        
        self.btn_test_gestures = ctk.CTkButton(self.gestures_preview_frame, text="Test Gestures (Open Window)", command=self._test_gestures)
        self.btn_test_gestures.pack(pady=20)
        
        self.btn_train_gesture = ctk.CTkButton(self.gestures_preview_frame, text="Train Custom Gesture (Coming Soon)", state="disabled")
        self.btn_train_gesture.pack(pady=10)

        # --- Triggers Frame ---
        self.triggers_frame = ctk.CTkFrame(self.container)
        self.triggers_label = ctk.CTkLabel(self.triggers_frame, text="Trigger Bindings", font=ctk.CTkFont(size=20, weight="bold"))
        self.triggers_label.pack(pady=10)
        
        # Header row
        header = ctk.CTkFrame(self.triggers_frame, fg_color="transparent")
        header.pack(fill="x", padx=20)
        ctk.CTkLabel(header, text="Target Macro", width=150, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Voice Command Word(s)", width=150, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Gesture", width=150, anchor="w").pack(side="left", padx=5)

        self.triggers_scroll = ctk.CTkScrollableFrame(self.triggers_frame, width=700, height=400)
        self.triggers_scroll.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.btn_add_trigger = ctk.CTkButton(self.triggers_frame, text="+ Add Trigger Binding", command=self._add_empty_trigger)
        self.btn_add_trigger.pack(pady=10, padx=20, side="left")
        self.btn_save_triggers = ctk.CTkButton(self.triggers_frame, text="Save Config", command=self._save_config, fg_color="green")
        self.btn_save_triggers.pack(pady=10, padx=20, side="right")

        self._load_config_to_ui()
        self._show_tab("dashboard")

    def _show_tab(self, tab_name):
        for frame in [self.dashboard_frame, self.settings_frame, self.macros_frame, self.gestures_frame, self.triggers_frame]:
            frame.pack_forget()
            
        if tab_name == "dashboard": self.dashboard_frame.pack(fill="both", expand=True)
        elif tab_name == "settings": self.settings_frame.pack(fill="both", expand=True)
        elif tab_name == "macros": self.macros_frame.pack(fill="both", expand=True)
        elif tab_name == "gestures": self.gestures_frame.pack(fill="both", expand=True)
        elif tab_name == "triggers": self.triggers_frame.pack(fill="both", expand=True)

    def _test_gestures(self):
        if self.control_queue:
            self.control_queue.put({"target": "gesture", "action": "toggle_preview", "value": True})
        self.update_log("External Gesture Camera Preview Opened")

    def _set_wake_word(self):
        new_word = self.wake_word_entry.get().strip()
        if new_word and self.control_queue:
            self.control_queue.put({"target": "voice", "action": "set_wake_word", "value": new_word})
            self.update_log(f"Wake word updated to: '{new_word}'")
            
    def _toggle_gesture(self):
        enabled = self.gesture_var.get()
        if self.cfg_manager:
            self.cfg_manager.config["engines"]["gesture"]["enabled"] = enabled
            self.cfg_manager.save(self.cfg_manager.config)
        if self.event_queue: self.event_queue.put({"engine": "gui", "label": "TOGGLE_GESTURES"})
        self.update_log(f"Gesture Engine state sent: {'Active' if enabled else 'Suspended'}")

    def _toggle_voice(self):
        enabled = self.voice_var.get()
        if self.cfg_manager:
            self.cfg_manager.config["engines"]["voice"]["enabled"] = enabled
            self.cfg_manager.save(self.cfg_manager.config)
        if self.event_queue: self.event_queue.put({"engine": "gui", "label": "TOGGLE_VOICE"})
        self.update_log(f"Voice Engine state sent: {'Active' if enabled else 'Suspended'}")

    # --- Config Loading ---
    def _load_config_to_ui(self):
        for row in self.hotkey_rows + self.ahk_rows + self.internal_rows + self.trigger_rows:
            row["frame"].destroy()
        self.hotkey_rows.clear()
        self.ahk_rows.clear()
        self.internal_rows.clear()
        self.trigger_rows.clear()
        
        # Clear Gestures List
        for widget in self.gestures_list_frame.winfo_children():
            widget.destroy()
            
        if self.cfg_manager:
            macros = self.cfg_manager.config.get("macros", {})
            for name, data in macros.items():
                if data.get("type") == "hotkey":
                    self._create_hotkey_row(name, data.get("value", ""))
                elif data.get("type") == "ahk":
                    self._create_ahk_row(name, data.get("value", ""))
                elif data.get("type") == "internal":
                    self._create_internal_row(name, data.get("value", ""))
            
            triggers = self.cfg_manager.config.get("triggers", {})
            for macro_name, data in triggers.items():
                self._create_trigger_row(macro_name, data.get("voice", ""), data.get("gesture", ""))
                
            gestures = self.cfg_manager.config.get("defined_gestures", [])
            for g in gestures:
                gf = ctk.CTkFrame(self.gestures_list_frame)
                gf.pack(fill="x", pady=2)
                ctk.CTkLabel(gf, text=g).pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(gf, text="Built-in", text_color="green").pack(side="right", padx=10)

    # --- Macros UI ---
    def _add_empty_hotkey(self):
        self._create_hotkey_row("New Hotkey", "")

    def _create_hotkey_row(self, name, value):
        row_frame = ctk.CTkFrame(self.hotkeys_scroll)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        name_entry = ctk.CTkEntry(row_frame, width=150)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=5)
        
        presets = ["volume up", "volume down", "volume mute", "play/pause media", "next track", "previous track", "Custom..."]
        value_var = ctk.StringVar(value="Custom..." if value not in presets and value else value)
        
        custom_entry = ctk.CTkEntry(row_frame, width=150)
        if value not in presets and value: custom_entry.insert(0, value)
            
        def on_preset_change(choice):
            if choice == "Custom...":
                custom_entry.pack(side="left", padx=5, fill="x", expand=True)
            else:
                custom_entry.pack_forget()
                
        preset_menu = ctk.CTkOptionMenu(row_frame, values=presets, variable=value_var, width=150, command=on_preset_change)
        preset_menu.pack(side="left", padx=5)
        
        if value_var.get() == "Custom...":
            custom_entry.pack(side="left", padx=5, fill="x", expand=True)
            
        def delete_row():
            row_frame.destroy()
            self.hotkey_rows = [r for r in self.hotkey_rows if r["frame"] != row_frame]
            
        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=delete_row)
        btn_del.pack(side="right", padx=5)
        
        self.hotkey_rows.append({"frame": row_frame, "name": name_entry, "preset": value_var, "custom": custom_entry})

    def _add_empty_ahk(self):
        self._create_ahk_row("New Script", "")

    def _create_ahk_row(self, name, value):
        row_frame = ctk.CTkFrame(self.ahk_scroll)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        name_entry = ctk.CTkEntry(row_frame, width=150)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=5)
        
        value_entry = ctk.CTkEntry(row_frame)
        value_entry.insert(0, value)
        value_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        def browse_file():
            filepath = ctk.filedialog.askopenfilename(filetypes=[("AutoHotkey Scripts", "*.ahk")])
            if filepath:
                value_entry.delete(0, "end")
                value_entry.insert(0, filepath)
                
        btn_browse = ctk.CTkButton(row_frame, text="Browse", width=60, command=browse_file)
        btn_browse.pack(side="left", padx=5)

        def delete_row():
            row_frame.destroy()
            self.ahk_rows = [r for r in self.ahk_rows if r["frame"] != row_frame]
            
        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=delete_row)
        btn_del.pack(side="right", padx=5)
        
        self.ahk_rows.append({"frame": row_frame, "name": name_entry, "value": value_entry})

    def _create_internal_row(self, name, value):
        row_frame = ctk.CTkFrame(self.internal_scroll)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        name_entry = ctk.CTkLabel(row_frame, text=name, width=150, anchor="w", font=ctk.CTkFont(weight="bold"))
        name_entry.pack(side="left", padx=5)
        
        value_entry = ctk.CTkLabel(row_frame, text=value, text_color="gray")
        value_entry.pack(side="left", padx=5)
        
        self.internal_rows.append({"frame": row_frame, "name_str": name})

    # --- Triggers UI ---
    def _add_empty_trigger(self):
        self._create_trigger_row("", "", "")

    def _create_trigger_row(self, macro_name, voice_word, gesture_name):
        row_frame = ctk.CTkFrame(self.triggers_scroll)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        # Current macros
        macro_names = [r["name"].get() for r in self.hotkey_rows + self.ahk_rows] + [r["name_str"] for r in self.internal_rows]
        if not macro_names and self.cfg_manager:
            macro_names = list(self.cfg_manager.config.get("macros", {}).keys())
            
        macro_menu = ctk.CTkComboBox(row_frame, values=macro_names, width=150)
        macro_menu.set(macro_name)
        macro_menu.pack(side="left", padx=5)
        
        voice_entry = ctk.CTkEntry(row_frame, width=150, placeholder_text="e.g. mute")
        voice_entry.insert(0, voice_word)
        voice_entry.pack(side="left", padx=5)
        
        gestures = self.cfg_manager.config.get("defined_gestures", []) if self.cfg_manager else []
        gesture_options = ["None"] + gestures
        gesture_menu = ctk.CTkOptionMenu(row_frame, values=gesture_options, width=150)
        gesture_menu.set(gesture_name if gesture_name else "None")
        gesture_menu.pack(side="left", padx=5)
        
        def delete_row():
            row_frame.destroy()
            self.trigger_rows = [r for r in self.trigger_rows if r["frame"] != row_frame]
            
        btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", command=delete_row)
        btn_del.pack(side="right", padx=5)
        
        self.trigger_rows.append({"frame": row_frame, "macro": macro_menu, "voice": voice_entry, "gesture": gesture_menu})

    def _save_config(self):
        if not self.cfg_manager: return
        
        new_macros = {}
        for row in self.hotkey_rows:
            n = row["name"].get().strip()
            p = row["preset"].get()
            v = row["custom"].get().strip() if p == "Custom..." else p
            if n and v: new_macros[n] = {"type": "hotkey", "value": v}
                
        for row in self.ahk_rows:
            n = row["name"].get().strip()
            v = row["value"].get().strip()
            if n and v: new_macros[n] = {"type": "ahk", "value": v}
                
        new_triggers = {}
        for row in self.trigger_rows:
            m = row["macro"].get().strip()
            v = row["voice"].get().strip()
            g = row["gesture"].get()
            if m:
                t_data = {}
                if v: t_data["voice"] = v
                if g and g != "None": t_data["gesture"] = g
                if t_data: new_triggers[m] = t_data

        self.cfg_manager.config["macros"] = new_macros
        self.cfg_manager.config["triggers"] = new_triggers
        self.cfg_manager.save(self.cfg_manager.config)
        
        if self.control_queue:
            self.event_queue.put({"engine": "gui", "label": "REFRESH_MAPPINGS"})
            
        self.update_log("Configuration saved and reloaded.")
        
        # Refresh UI to update macro dropdowns in triggers tab
        self._load_config_to_ui()

    def update_log(self, message):
        if hasattr(self, 'log_view'):
            self.log_view.insert("end", f"> {message}\n")
            self.log_view.see("end")

    def run(self):
        self.mainloop()
