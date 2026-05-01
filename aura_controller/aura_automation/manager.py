"""
Aura Automation Manager
Maps triggers from the engines to actual Windows actions.
"""

import os
import subprocess
import keyboard # External library for hotkey emulation

class AutomationManager:
    def __init__(self, mapping_config: dict):
        """
        mapping_config: Dictionary mapping labels to action definitions.
        Example: {"VOLUME_UP": {"type": "hotkey", "value": "volume up"}}
        """
        self.mappings = mapping_config
        self.ahk_path = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"

    def execute(self, trigger_label: str):
        """
        Lookup the action for a trigger and execute it.
        """
        action = self.mappings.get(trigger_label)
        if not action:
            return

        action_type = action.get("type")
        value = action.get("value")

        if action_type == "hotkey":
            self._send_hotkey(value)
        elif action_type == "ahk":
            self._run_ahk(value)
        elif action_type == "shell":
            self._run_shell(value)

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

    def _run_shell(self, command: str):
        """Runs a system shell command."""
        try:
            subprocess.Popen(command, shell=True)
            print(f"Executed Shell: {command}")
        except Exception as e:
            print(f"Shell Error: {e}")
