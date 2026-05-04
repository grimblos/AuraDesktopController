"""
Aura Automation Manager
Maps triggers from the engines to actual Windows actions.
"""

import os
import subprocess
import keyboard # External library for hotkey emulation

class AutomationManager:
    def __init__(self, macros: dict, triggers: dict):
        """
        macros: Dictionary of named macros and their actions.
        triggers: Dictionary mapping macro names to their voice/gesture triggers.
        """
        self.ahk_path = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"
        self.gesture_suspended = False
        self.voice_suspended = False
        self.reload(macros, triggers)

    def reload(self, macros: dict, triggers: dict):
        """Rebuilds the internal state and lookup table."""
        self.macros = macros
        self.triggers = triggers
        self._lookup = {}
        
        for macro_name, trigger_data in triggers.items():
            voice_word = trigger_data.get("voice")
            gesture_name = trigger_data.get("gesture")
            
            if voice_word:
                voice_label = f"VOICE_{voice_word.upper().replace(' ', '_')}"
                self._lookup[voice_label] = macro_name
                
            if gesture_name:
                gesture_label = f"GESTURE_{gesture_name.upper()}"
                self._lookup[gesture_label] = macro_name

    def execute(self, trigger_label: str):
        """
        Lookup the macro for a formatted trigger (e.g., GESTURE_FIST) and execute it.
        Respects functional suspension.
        """
        macro_name = self._lookup.get(trigger_label)
        if not macro_name:
            # Check if this is a direct internal command call from the GUI
            if trigger_label.startswith("GUI_"):
                cmd = trigger_label.replace("GUI_", "")
                if cmd in ["TOGGLE_GESTURES", "TOGGLE_VOICE", "SLEEP_ALL", "WAKE_ALL"]:
                    self._run_internal(cmd)
            return
            
        action = self.macros.get(macro_name)
        if not action:
            print(f"Warning: Trigger mapped to unknown macro '{macro_name}'")
            return

        action_type = action.get("type")
        value = action.get("value")
        
        # Determine if the current engine is suspended
        is_gesture = trigger_label.startswith("GESTURE_")
        is_voice = trigger_label.startswith("VOICE_")
        
        if (is_gesture and self.gesture_suspended) or (is_voice and self.voice_suspended):
            # If suspended, ONLY allow internal wake/toggle commands
            if action_type != "internal" or value not in ["TOGGLE_GESTURES", "TOGGLE_VOICE", "WAKE_ALL"]:
                return # Blocked by suspension

        if action_type == "hotkey":
            self._send_hotkey(value)
        elif action_type == "ahk":
            self._run_ahk(value)
        elif action_type == "internal":
            self._run_internal(value)

    def _run_internal(self, command: str):
        """Processes internal commands like functional sleep/wake."""
        if command == "TOGGLE_GESTURES":
            self.gesture_suspended = not self.gesture_suspended
            print(f"Gestures Suspended: {self.gesture_suspended}")
        elif command == "TOGGLE_VOICE":
            self.voice_suspended = not self.voice_suspended
            print(f"Voice Suspended: {self.voice_suspended}")
        elif command == "SLEEP_ALL":
            self.gesture_suspended = True
            self.voice_suspended = True
            print("Aura entering functional sleep mode...")
        elif command == "WAKE_ALL":
            self.gesture_suspended = False
            self.voice_suspended = False
            print("Aura functional wake...")

    def _send_hotkey(self, key_combo: str):
        """Emulates a physical keyboard press."""
        try:
            keyboard.press_and_release(key_combo)
            print(f"Executed Hotkey: {key_combo}")
        except Exception as e:
            print(f"Hotkey Error: {e}")

    def _run_ahk(self, script_path: str):
        """Executes an AutoHotkey script."""
        if os.path.exists(self.ahk_path):
            try:
                subprocess.Popen([self.ahk_path, script_path])
                print(f"Executed AHK: {script_path}")
            except Exception as e:
                print(f"AHK Error: {e}")

