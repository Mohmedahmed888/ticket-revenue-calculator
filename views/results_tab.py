import customtkinter as ctk
from tkinter import messagebox
import datetime

class ResultsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        results_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        title = ctk.CTkLabel(results_frame, text="Maximum Revenue", font=("Arial", 24, "bold"), text_color="white")
        title.pack(pady=15)
        
        self.result_entry = ctk.CTkEntry(results_frame, font=("Arial", 36, "bold"), height=70, justify="center", state="readonly", text_color="#4CAF50")
        self.result_entry.pack(pady=(5, 20), padx=20, fill="x")
        self.result_entry.insert(0, "0")
        
        details_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        left_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        left_details.pack(side="left", fill="x", expand=True)
        
        self.prices_label = ctk.CTkLabel(left_details, text="Prices: -", font=("Arial", 14), anchor="w", text_color="white")
        self.prices_label.pack(fill="x", pady=2)
        
        self.tickets_label = ctk.CTkLabel(left_details, text="Number of Tickets: -", font=("Arial", 14), anchor="w", text_color="white")
        self.tickets_label.pack(fill="x", pady=2)
        
        right_details = ctk.CTkFrame(details_frame, fg_color="transparent")
        right_details.pack(side="right", fill="x", expand=True)
        
        self.algo_label = ctk.CTkLabel(right_details, text="Algorithm: -", font=("Arial", 14), anchor="w", text_color="white")
        self.algo_label.pack(fill="x", pady=2)
        
        self.time_label = ctk.CTkLabel(right_details, text="Time: -", font=("Arial", 14), anchor="w", text_color="white")
        self.time_label.pack(fill="x", pady=2)
        
        complexity_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        complexity_frame.pack(fill="x", padx=20, pady=10)
        
        self.time_complexity_label = ctk.CTkLabel(complexity_frame, text="Time Complexity: -", font=("Arial", 14), anchor="w", text_color="white")
        self.time_complexity_label.pack(fill="x", pady=2)
        
        self.space_complexity_label = ctk.CTkLabel(complexity_frame, text="Space Complexity: -", font=("Arial", 14), anchor="w", text_color="white")
        self.space_complexity_label.pack(fill="x", pady=2)
        
        steps_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        steps_frame.pack(fill="x", padx=20, pady=10)
        
        steps_title = ctk.CTkLabel(steps_frame, text="Algorithm Steps:", font=("Arial", 16, "bold"), text_color="white")
        steps_title.pack(anchor="w", pady=5)
        
        self.steps_label = ctk.CTkLabel(steps_frame, text="-", font=("Arial", 14), justify="left", text_color="white")
        self.steps_label.pack(anchor="w", pady=5)
        
        save_button = ctk.CTkButton(results_frame, text="Save Results", font=("Arial", 14, "bold"), command=self.save_current_results)
        save_button.pack(pady=20)

    def update_display(self, revenue, prices, total_tickets, algorithm, duration, complexity, space, description):
        """Update all the labels and entry fields in this tab."""
        self.result_entry.configure(state="normal")
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, f"{revenue:,}")
        self.result_entry.configure(state="readonly")
        
        self.prices_label.configure(text=f"Prices: {', '.join(map(str, sorted(prices, reverse=True)))}")
        self.tickets_label.configure(text=f"Number of Tickets: {total_tickets}")
        self.algo_label.configure(text=f"Algorithm: {algorithm.replace('_', ' ').title()}")
        self.time_label.configure(text=f"Time: {duration:.4f} seconds")
        self.time_complexity_label.configure(text=f"Time Complexity: {complexity}")
        self.space_complexity_label.configure(text=f"Space Complexity: {space}")
        self.steps_label.configure(text=description)

    def save_current_results(self):
        """Save the currently displayed results to the database."""
        try:
            revenue_str = self.result_entry.get().replace(",", "")
            if not revenue_str or revenue_str == '0':
                messagebox.showwarning("Save Info", "No calculation results available to save.")
                return
                
            revenue = int(revenue_str)
            prices_str = self.prices_label.cget("text").replace("Prices: ", "")
            tickets = int(self.tickets_label.cget("text").replace("Number of Tickets: ", ""))
            method = self.algo_label.cget("text").replace("Algorithm: ", "")
            duration_str = self.time_label.cget("text").replace("Time: ", "").replace(" seconds", "")
            duration = float(duration_str) if duration_str != '-' else 0.0
            
            success = self.app.db.save_result(
                timestamp=datetime.datetime.now(), 
                prices_str=prices_str,
                tickets=tickets, 
                revenue=revenue, 
                method=method, 
                duration=duration
            )
            
            if success:
                if hasattr(self.app, 'history_tab_instance'):
                    self.app.history_tab_instance.load_history_data()
                messagebox.showinfo("Success", "Result saved successfully!")
                self.app.sound_manager.play_sound("success")
            else:
                messagebox.showerror("Save Error", "Failed to save result. Database connection might be closed.")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save result: {str(e)}")
            self.app.sound_manager.play_sound("error") 