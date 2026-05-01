"""
Aura Command Router
Distinguishes between internal app controls and external automations.
"""

class CommandRouter:
    def __init__(self, app_instance):
        self.app = app_instance
        
    def route(self, trigger_label: str):
        """
        Receives a trigger (e.g., 'MUTE_MIC') and decides where it goes.
        """
        if trigger_label.startswith("APP_"):
            self._handle_internal(trigger_label)
        else:
            self._handle_external(trigger_label)
            
    def _handle_internal(self, command: str):
        """Controls Aura itself (e.g., APP_STOP_GESTURE)."""
        pass
        
    def _handle_external(self, trigger: str):
        """Triggers AHK, Hotkeys, etc."""
        pass
