"""
Aura Command Router
Distinguishes between internal app controls and external automations.
"""

class CommandRouter:
    def __init__(self, automation_manager, control_queue):
        self.automation_manager = automation_manager
        self.control_queue = control_queue
        
        # Internal Command Mapping
        self.internal_commands = {}
        
    def route(self, trigger_label: str, engine_name: str = None):
        """
        Receives a trigger (e.g., 'MUTE') and decides where it goes.
        If an external action, prepends engine_name (e.g., 'VOICE_MUTE').
        """
        print(f"Routing Trigger: {trigger_label} (Engine: {engine_name})")
        
        # Format label for triggers dict (e.g. "GESTURE_FIST")
        formatted_label = trigger_label
        if engine_name:
            formatted_label = f"{engine_name.upper()}_{trigger_label}"
            
        self.automation_manager.execute(formatted_label)
