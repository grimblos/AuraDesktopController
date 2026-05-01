"""
Aura OSD (On-Screen Display)
A translucent, always-on-top overlay for visual feedback.
"""

import customtkinter as ctk

class AuraOSD(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure window as an overlay
        self.overrideredirect(True) # Remove borders
        self.attributes("-topmost", True) # Always on top
        self.attributes("-alpha", 0.8) # Translucency
        
        # Position in top-right corner
        screen_width = self.winfo_screenwidth()
        self.geometry(f"250x60+{screen_width - 270}+50")
        
        self.frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        self.frame.pack(fill="both", expand=True)
        
        self.label = ctk.CTkLabel(self.frame, text="Aura Ready", font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(pady=15)
        
        self.withdraw() # Start hidden

    def show_trigger(self, label: str, duration_ms: int = 2000):
        """Display a trigger message briefly."""
        self.label.configure(text=f"Trigger: {label}")
        self.deiconify()
        self.after(duration_ms, self.withdraw)
