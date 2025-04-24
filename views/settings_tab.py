import customtkinter as ctk

class SettingsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(frame, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        settings_frame = ctk.CTkFrame(frame)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        appearance_label = ctk.CTkLabel(settings_frame, text="Appearance Settings:", font=ctk.CTkFont(size=16, weight="bold"))
        appearance_label.pack(fill="x", padx=15, pady=(15, 5))
        
        # Get initial mode from DB via app.db
        initial_mode = self.app.db.get_setting("appearance_mode", "dark") 
        self.appearance_mode_var = ctk.StringVar(value=initial_mode.capitalize()) # Use var to hold state
        appearance_menu = ctk.CTkOptionMenu(
            settings_frame, values=["Light", "Dark", "System"],
            command=self.change_appearance_mode,
            variable=self.appearance_mode_var, # Use the variable here
            width=200, height=32, dynamic_resizing=False
        )
        appearance_menu.pack(padx=15, pady=(0, 15))
        
        separator1 = ctk.CTkFrame(settings_frame, height=2)
        separator1.pack(fill="x", padx=15, pady=10)
        
        sound_label = ctk.CTkLabel(settings_frame, text="Sound Settings:", font=ctk.CTkFont(size=16, weight="bold"))
        sound_label.pack(fill="x", padx=15, pady=5)
        
        # Get initial sound state from SoundManager instance
        self.sound_var = ctk.BooleanVar(value=self.app.sound_manager.enabled) 
        sound_checkbox = ctk.CTkCheckBox(
            settings_frame, text="Enable Sounds", variable=self.sound_var,
            font=ctk.CTkFont(size=14), checkbox_width=24, checkbox_height=24,
            command=self.toggle_sound # Link command
        )
        sound_checkbox.pack(padx=15, pady=(0, 15))
        
        separator2 = ctk.CTkFrame(settings_frame, height=2)
        separator2.pack(fill="x", padx=15, pady=10)
        
        info_frame = ctk.CTkFrame(settings_frame)
        info_frame.pack(fill="x", padx=15, pady=5)
        app_info_label = ctk.CTkLabel(info_frame, text="App Information:", font=ctk.CTkFont(size=16, weight="bold"))
        app_info_label.pack(fill="x", pady=5)
        version_label = ctk.CTkLabel(info_frame, text="App Version: 1.0.0", font=ctk.CTkFont(size=14))
        version_label.pack(fill="x", pady=2)
        dev_label = ctk.CTkLabel(info_frame, text="Developed by: Your Team", font=ctk.CTkFont(size=14)) # Placeholder
        dev_label.pack(fill="x", pady=2)

    def change_appearance_mode(self, new_mode_capitalized: str):
        """Called when the OptionMenu changes."""
        new_mode_lower = new_mode_capitalized.lower()
        ctk.set_appearance_mode(new_mode_lower)
        self.app.db.save_setting("appearance_mode", new_mode_lower)
        # Update plot colors if analytics tab exists and is initialized
        if hasattr(self.app, 'analytics_tab_instance') and self.app.analytics_tab_instance.fig:
            self.app.analytics_tab_instance.update_plot()

    def toggle_sound(self):
        """Called when the Checkbox state changes."""
        is_enabled = self.sound_var.get()
        # Use the toggle method in SoundManager, passing the save function
        self.app.sound_manager.toggle_sounds(is_enabled, self.app.db.save_setting) 