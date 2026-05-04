"""
Aura Config Manager
Handles loading, saving, and validation of the config.json file.
"""

import json
import os

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.defaults = {
            "mode": "local",
            "server": {
                "ip": "127.0.0.1",
                "port": 5005,
                "auto_discovery": True,
                "encryption": {"enabled": False, "secret_key": ""}
            },
            "engines": {
                "gesture": {"enabled": True, "fps_cap": 20, "camera_id": 0},
                "voice": {"enabled": True, "model_path": "models/vosk-model-small-en-us-0.15", "wake_word": "aura"}
            },
            "defined_gestures": [
                "PALM_OPEN",
                "FIST",
                "POINTING",
                "PEACE_SIGN",
                "THUMBS_UP",
                "ROCK_ON"
            ],
            "macros": {
                "Toggle Gestures": {"type": "internal", "value": "TOGGLE_GESTURES"},
                "Toggle Voice": {"type": "internal", "value": "TOGGLE_VOICE"},
                "Sleep All": {"type": "internal", "value": "SLEEP_ALL"},
                "Wake All": {"type": "internal", "value": "WAKE_ALL"},
                "Volume Up": {"type": "hotkey", "value": "volume up"},
                "Volume Down": {"type": "hotkey", "value": "volume down"},
                "Mute Audio": {"type": "hotkey", "value": "volume mute"}
            },
            "triggers": {
                "Mute Audio": { "voice": "mute", "gesture": "FIST" },
                "Volume Up":  { "voice": "volume up", "gesture": "PALM_OPEN" },
                "Volume Down": { "voice": "volume down", "gesture": "POINTING" }
            }
        }
        self.config = self.load()

    def load(self):
        """Loads config from file or returns defaults."""
        if not os.path.exists(self.config_path):
            self.save(self.defaults)
            return self.defaults
        
        try:
            with open(self.config_path, "r") as f:
                loaded = json.load(f)
                # Merge with defaults to ensure missing keys are present
                return self._merge_defaults(self.defaults, loaded)
        except Exception as e:
            print(f"Config Load Error: {e}")
            return self.defaults

    def save(self, config_data):
        """Saves config to file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Config Save Error: {e}")

    def _merge_defaults(self, defaults, loaded):
        """Recursively merge defaults into loaded config."""
        for key, value in defaults.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict):
                loaded[key] = self._merge_defaults(value, loaded[key])
        return loaded
