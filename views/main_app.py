import customtkinter as ctk
import matplotlib.pyplot as plt
import datetime
from tkinter import messagebox
import os

from utils import Database
from utils import SoundManager
from algorithms import (
    brute_force_max_revenue,
    dynamic_programming_max_revenue,
    optimized_greedy_max_revenue
)

from .calculator_tab import CalculatorTab
from .results_tab import ResultsTab
from .analytics_tab import AnalyticsTab
from .history_tab import HistoryTab
from .settings_tab import SettingsTab

class TicketRevenueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        print("TicketRevenueApp: Initializing...")
        self.title("Ticket Revenue Calculator")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        self._is_closing = False
        self.current_revenue = 0 # To store the result between calculation and saving
        
        # Initialize Utilities
        self.db = Database() 
        self.sound_manager = SoundManager() 
        # Load initial settings from DB
        self._load_initial_settings()

        # --- Create UI --- 
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs (just the frames first)
        self.tab_calculator_frame = self.tabview.add("Calculator")
        self.tab_results_frame = self.tabview.add("Results")
        self.tab_analytics_frame = self.tabview.add("Analytics")
        self.tab_history_frame = self.tabview.add("History")
        self.tab_settings_frame = self.tabview.add("Settings")
        
        # Instantiate Tab Classes (pass the corresponding frame and self)
        # Store instances with distinct names to access them later
        self.calculator_tab_instance = CalculatorTab(self.tab_calculator_frame, self)
        self.results_tab_instance = ResultsTab(self.tab_results_frame, self)
        self.analytics_tab_instance = AnalyticsTab(self.tab_analytics_frame, self)
        self.history_tab_instance = HistoryTab(self.tab_history_frame, self)
        self.settings_tab_instance = SettingsTab(self.tab_settings_frame, self)
        
        # Set default tab
        self.tabview.set("Calculator")
        
        # Bind closing event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _load_initial_settings(self):
        """Load appearance and sound settings from DB."""
        initial_mode = self.db.get_setting("appearance_mode", "dark")
        ctk.set_appearance_mode(initial_mode)
        
        initial_sound_str = self.db.get_setting("sound_enabled", "True")
        initial_sound_bool = initial_sound_str.lower() == 'true'
        # Update SoundManager state based on DB
        self.sound_manager.enabled = initial_sound_bool 
        os.environ['ENABLE_SOUNDS'] = str(initial_sound_bool).lower() # Keep env var sync (optional)

    def calculate_revenue(self):
        """Handles the main calculation logic triggered by CalculatorTab button."""
        try:
            # Get inputs from CalculatorTab instance
            prices, total_tickets, algorithm = self.calculator_tab_instance.get_inputs()
            
            # Show progress bar via CalculatorTab instance
            self.calculator_tab_instance.show_progress()
            self.update_idletasks() # Ensure UI updates before long calculation
            
            start_time = datetime.datetime.now()
            revenue = 0
            used_prices = []
            complexity = "N/A"
            space = "N/A"
            description = "Algorithm not found."
            
            # Call the correct algorithm function
            if algorithm == "brute_force":
                revenue = brute_force_max_revenue(prices, total_tickets)
                # Brute force in trk.py didn't return used_prices
                complexity = "O(n^k)"; space = "O(k)" # Example complexities
                description = "1. Sort prices desc\n2. Try all combinations (recursive with memoization)\n3. Enforce price order constraint\n4. Return max revenue"
            elif algorithm == "dynamic":
                revenue, used_prices = dynamic_programming_max_revenue(prices, total_tickets)
                complexity = "O(n*k)"; space = "O(n*k)"
                description = "1. Sort prices desc\n2. Create DP table n*k\n3. Fill table using optimal substructure\n4. Track used prices via path table\n5. Return max revenue & prices"
            elif algorithm == "greedy": 
                revenue, used_prices = optimized_greedy_max_revenue(prices, total_tickets)
                complexity = "O(n log n)"; space = "O(n)"
                description = "1. Sort prices desc\n2. Iterate through sorted prices\n3. Use current price, move to next or stay based on 1.5x rule\n4. Return revenue & prices"
            
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.current_revenue = revenue # Store for saving later
            
            # Update the Results Tab display via its instance
            self.results_tab_instance.update_display(
                revenue, prices, total_tickets, algorithm, duration,
                complexity, space, description
            )
            
            # Update the Analytics Tab plot via its instance
            self.analytics_tab_instance.update_plot()
            
            self.sound_manager.play_sound("success")
            self.tabview.set("Results") # Switch view to Results tab
            
        except ValueError as ve: # Catch specific validation errors
            messagebox.showerror("Input Error", str(ve))
            self.sound_manager.play_sound("error")
        except Exception as e: # Catch other calculation errors
            messagebox.showerror("Calculation Error", f"An error occurred: {str(e)}")
            self.sound_manager.play_sound("error")
        finally:
            # Hide progress bar via CalculatorTab instance
            self.calculator_tab_instance.hide_progress()

    def on_closing(self):
        """Handle application closing cleanly."""
        if self._is_closing:
            return
        self._is_closing = True
        print("Starting on_closing process...") # Debug

        try:
            # Process any pending UI events first
            print("Running update_idletasks...") # Debug
            self.update_idletasks()
            
            # Stop progress bar if running 
            if hasattr(self, 'calculator_tab_instance'):
                print("Hiding progress bar...") # Debug
                self.calculator_tab_instance.hide_progress() 
                
            # Cancel all pending .after() jobs 
            print("Cancelling pending .after() jobs...") # Debug
            for widget in self.winfo_children():
                if widget.winfo_exists():
                    try:
                        widget.after_cancel('all')
                    except Exception as e_cancel:
                        print(f"Minor error during after_cancel for {widget}: {e_cancel}")
                       
        except Exception as e:
            print(f"Error during initial cleanup (progress/cancel jobs): {e}")
            
        # Close database connection
        try:
            if hasattr(self, 'db') and self.db:
                print("Closing database...") # Debug
                self.db.close()
        except Exception as e:
             print(f"Error closing database during close: {e}")

        # Close Matplotlib figures
        try:
            print("Closing matplotlib plots...") # Debug
            plt.close('all')
        except Exception as e:
            print(f"Error closing plots during close: {e}")

        # Quit the Tkinter main loop
        try:
            print("Quitting main loop...") # Debug
            self.quit()
        except Exception as e:
            print(f"Error quitting main loop: {e}")
            
        # Destroy the main window
        # Use after(10, ...) to give time for quit to process before destroying
        print("Scheduling final destroy...") # Debug
        self.after(10, self._final_destroy)

    def _final_destroy(self):
        """Helper function to destroy the window after a short delay."""
        try:
            print("Executing final destroy...") # Debug
            self.destroy() 
            print("Window destroyed.") # Debug
        except Exception as e:
             print(f"Error during final destroy: {e}") 