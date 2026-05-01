"""
Aura Command Router
Distinguishes between internal app controls and external automations.
"""

class CommandRouter:
    def __init__(self, automation_manager, control_queue):
        self.automation_manager = automation_manager
        self.control_queue = control_queue
        
        # Internal Command Mapping
        self.internal_commands = {
            "APP_STOP_GESTURE": lambda: self.control_queue.put({"target": "gesture", "action": "stop"}),
            "APP_START_GESTURE": lambda: self.control_queue.put({"target": "gesture", "action": "start"}),
            "APP_STOP_VOICE": lambda: self.control_queue.put({"target": "voice", "action": "stop"}),
            "APP_START_VOICE": lambda: self.control_queue.put({"target": "voice", "action": "start"}),
            "APP_SLEEP": self._go_to_sleep,
            "APP_WAKE": self._wake_up
        }
        
    def route(self, trigger_label: str):
        """
        Receives a trigger (e.g., 'MUTE_MIC') and decides where it goes.
        """
        print(f"Routing Trigger: {trigger_label}")
        
        if trigger_label in self.internal_commands:
            self.internal_commands[trigger_label]()
        else:
            # If not an internal command, pass to the automation manager
            self.automation_manager.execute(trigger_label)
            
    def _go_to_sleep(self):
        """Disables both engines."""
        self.control_queue.put({"target": "gesture", "action": "stop"})
        self.control_queue.put({"target": "voice", "action": "stop"})
        print("Aura entering sleep mode...")

    def _wake_up(self):
        """Enables both engines."""
        self.control_queue.put({"target": "gesture", "action": "start"})
        self.control_queue.put({"target": "voice", "action": "start"})
        print("Aura waking up...")
