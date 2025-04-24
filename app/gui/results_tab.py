import customtkinter as ctk
from datetime import datetime

class ResultsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_results_tab()
    
    def create_results_tab(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Results frame
        results_frame = ctk.CTkFrame(main_frame, fg_color="#2b2b2b")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Title
        title = ctk.CTkLabel(
            results_frame,
            text="Maximum Revenue",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        title.pack(pady=15)
        
        # Revenue display
        self.result_entry = ctk.CTkEntry(
            results_frame,
            font=("Arial", 36, "bold"),
            height=70,
            justify="center",
            state="readonly",
            text_color="#4CAF50",
            fg_color="#1a1a1a",
            border_color="#404040"
        )
        self.result_entry.pack(pady=(5, 20), padx=20, fill="x")
        self.result_entry.insert(0, "0")
        
        # Details frame
        details_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Left details
        left_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        left_details.pack(side="left", fill="x", expand=True)
        
        self.prices_label = ctk.CTkLabel(
            left_details,
            text="Prices: -",
            font=("Arial", 14),
            anchor="w",
            text_color="#e0e0e0"
        )
        self.prices_label.pack(fill="x", pady=2)
        
        self.tickets_label = ctk.CTkLabel(
            left_details,
            text="Number of Tickets: -",
            font=("Arial", 14),
            anchor="w",
            text_color="#e0e0e0"
        )
        self.tickets_label.pack(fill="x", pady=2)
        
        # Right details
        right_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        right_details.pack(side="right", fill="x", expand=True)
        
        self.algo_label = ctk.CTkLabel(
            right_details,
            text="Algorithm: -",
            font=("Arial", 14),
            anchor="w",
            text_color="#e0e0e0"
        )
        self.algo_label.pack(fill="x", pady=2)
        
        self.time_label = ctk.CTkLabel(
            right_details,
            text="Time: -",
            font=("Arial", 14),
            anchor="w",
            text_color="#e0e0e0"
        )
        self.time_label.pack(fill="x", pady=2)
        
        # Complexity frame
        complexity_frame = ctk.CTkFrame(results_frame, fg_color="#1a1a1a")
        complexity_frame.pack(fill="x", padx=20, pady=10)
        
        self.time_complexity_label = ctk.CTkLabel(
            complexity_frame,
            text="Time Complexity: -",
            font=("Arial", 14),
            anchor="w",
            text_color="#e0e0e0"
        )
        self.time_complexity_label.pack(fill="x", pady=2)
        
        self.space_complexity_label = ctk.CTkLabel(
            complexity_frame,
            text="Space Complexity: -",
            font=("Arial", 14),
            anchor="w",
            text_color="#e0e0e0"
        )
        self.space_complexity_label.pack(fill="x", pady=2)
        
        # Algorithm steps frame
        steps_frame = ctk.CTkFrame(results_frame, fg_color="#1a1a1a")
        steps_frame.pack(fill="x", padx=20, pady=10)
        
        steps_title = ctk.CTkLabel(
            steps_frame,
            text="Algorithm Steps:",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        steps_title.pack(anchor="w", pady=5)
        
        self.steps_label = ctk.CTkLabel(
            steps_frame,
            text="-",
            font=("Arial", 14),
            justify="left",
            text_color="#e0e0e0"
        )
        self.steps_label.pack(anchor="w", pady=5)
        
        # Save results button
        save_button = ctk.CTkButton(
            results_frame,
            text="Save Results",
            font=("Arial", 14, "bold"),
            command=self.save_results,
            fg_color="#404040",
            hover_color="#505050",
            text_color="white"
        )
        save_button.pack(pady=20) 