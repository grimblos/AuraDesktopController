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

        self.btn_mappings = ctk.CTkButton(self.sidebar, text="Mappings", command=lambda: self._show_tab("mappings"))
        self.btn_mappings.pack(pady=10, padx=20)

        # Main Content Area
        self.main_content = ctk.CTkFrame(self, corner_radius=15)
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self._init_dashboard()

    def _init_dashboard(self):
        """Dashboard Tab: Status indicators and real-time logs."""
        self.clear_main_content()
        
        lbl = ctk.CTkLabel(self.main_content, text="System Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=20)

        # Status Cards Frame
        self.cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20)

        # Example Status Card
        self.gesture_status = self._create_status_card(self.cards_frame, "Gesture Engine", "Active (Local)", "green")
        self.voice_status = self._create_status_card(self.cards_frame, "Voice Engine", "Active (Remote)", "blue")

        # Log View
        self.log_view = ctk.CTkTextbox(self.main_content, height=300)
        self.log_view.pack(fill="both", expand=True, padx=20, pady=20)
        self.log_view.insert("0.0", "Aura System Initialized...\nListening for triggers...")

    def _create_status_card(self, parent, title, status, color):
        card = ctk.CTkFrame(parent, width=200, height=100)
        card.pack(side="left", padx=10, expand=True)
        
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        lbl_title.pack(pady=(10, 0))
        
        lbl_status = ctk.CTkLabel(card, text=status, text_color=color, font=ctk.CTkFont(weight="bold"))
        lbl_status.pack(pady=10)
        return lbl_status

    def _show_tab(self, tab_name):
        if tab_name == "dashboard": self._init_dashboard()
        # TODO: Implement Settings and Mappings tab views

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def update_log(self, message):
        self.log_view.insert("end", f"\n{message}")
        self.log_view.see("end")
