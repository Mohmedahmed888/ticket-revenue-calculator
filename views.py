import customtkinter as ctk
import datetime
from tkinter import messagebox
import matplotlib.pyplot as plt
from algorithms import brute_force_max_revenue, dynamic_programming_max_revenue, optimized_greedy_max_revenue
from utils import Database, SoundManager

# --- Calculator Tab ---

class CalculatorTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_calculator_tab()
    
    def create_calculator_tab(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        input_title = ctk.CTkLabel(input_frame, text="Enter Ticket Prices", font=("Arial", 20, "bold"))
        input_title.pack(pady=10)
        
        self.price_entries = []
        entries_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        entries_frame.pack(fill="x", padx=20, pady=10)
        
        for row in range(3):
            row_frame = ctk.CTkFrame(entries_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure((0,1,2), weight=1)
            for col in range(3):
                entry = ctk.CTkEntry(row_frame, placeholder_text=f"Price {row*3 + col + 1}", font=ctk.CTkFont(size=13), height=35)
                entry.grid(row=0, column=col, padx=5, sticky="ew")
                self.price_entries.append(entry)
        
        tickets_frame = ctk.CTkFrame(input_frame)
        tickets_frame.pack(pady=10, padx=20, fill="x")
        tickets_label = ctk.CTkLabel(tickets_frame, text="Number of Tickets:", font=ctk.CTkFont(size=14))
        tickets_label.pack(side="left", padx=10, pady=10)
        self.tickets_entry = ctk.CTkEntry(tickets_frame, width=100, height=35, font=ctk.CTkFont(size=13))
        self.tickets_entry.pack(side="left", padx=10, pady=10)
        
        algo_frame = ctk.CTkFrame(input_frame)
        algo_frame.pack(pady=10, padx=20, fill="x")
        algo_label = ctk.CTkLabel(algo_frame, text="Select Algorithm:", font=ctk.CTkFont(size=14))
        algo_label.pack(side="left", padx=10, pady=10)
        self.algorithm_var = ctk.StringVar(value="brute_force")
        algorithms = [("Brute Force", "brute_force"), ("Dynamic Programming", "dynamic"), ("Optimized Greedy", "greedy")]
        radio_frame = ctk.CTkFrame(algo_frame, fg_color="transparent")
        radio_frame.pack(side="left", fill="x", expand=True, padx=10)
        for text, value in algorithms:
            radio = ctk.CTkRadioButton(radio_frame, text=text, value=value, variable=self.algorithm_var, font=ctk.CTkFont(size=13))
            radio.pack(side="left", padx=10)
        
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=5)
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.set(0)
        
        calculate_button = ctk.CTkButton(main_frame, text="Calculate Maximum Revenue ▶", font=("Arial", 18, "bold"), height=50, command=self.calculate_revenue)
        calculate_button.pack(pady=20)
    
    def calculate_revenue(self):
        try:
            self.progress_bar.pack(fill="x", padx=10, pady=5)
            self.progress_bar.start()
            prices = []
            for entry in self.price_entries:
                value = entry.get().strip()
                if value:
                    try:
                        price = int(value)
                        if price <= 0:
                            raise ValueError("Prices must be positive numbers")
                        prices.append(price)
                    except ValueError:
                        raise ValueError("Please enter valid numbers for prices")
            try:
                total_tickets = int(self.tickets_entry.get())
                if total_tickets <= 0:
                    raise ValueError("Number of tickets must be positive")
                elif total_tickets > 1000:
                    raise ValueError("Maximum number of tickets is 1000")
            except ValueError as e:
                if "Maximum number" in str(e):
                    raise e
                raise ValueError("Please enter a valid number of tickets")
            if not prices:
                raise ValueError("Please enter at least one price")
            
            algorithm = self.algorithm_var.get()
            start_time = datetime.datetime.now()
            
            if algorithm == "brute_force":
                revenue = brute_force_max_revenue(prices, total_tickets)
                used_prices = []
                complexity = "O(n^k)"; space = "O(k)"
                description = "1. Sort prices desc\n2. Try all combinations\n3. Memoize results\n4. Return max revenue"
            elif algorithm == "dynamic":
                revenue, used_prices = dynamic_programming_max_revenue(prices, total_tickets)
                complexity = "O(n*k)"; space = "O(n*k)"
                description = "1. Sort prices desc\n2. Create DP table n*k\n3. Fill table\n4. Track used prices\n5. Return max revenue & prices"
            else: # greedy
                revenue, used_prices = optimized_greedy_max_revenue(prices, total_tickets)
                complexity = "O(n log n)"; space = "O(n)"
                description = "1. Sort prices desc\n2. Start with highest\n3. Decide based on next price\n4. Move to next\n5. Return revenue & prices"
            
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.app.current_revenue = revenue
            
            # Use self.app.results_tab (assuming it's created in main window)
            self.app.results_tab.update_results(
                revenue=revenue, prices=prices, total_tickets=total_tickets,
                algorithm=algorithm, duration=duration, complexity=complexity,
                space=space, description=description
            )
            
            # Assume self.app.analytics_tab exists
            # self.app.analytics_tab.update_analytics(prices, revenue)
            
            self.app.sound_manager.play_sound("success")
            self.app.tabview.set("Results")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.app.sound_manager.play_sound("error")
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    def clear_fields(self):
        for entry in self.price_entries:
            entry.delete(0, "end")
        self.tickets_entry.delete(0, "end")

# --- Results Tab ---

class ResultsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_results_tab()
    
    def create_results_tab(self):
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
        
        save_button = ctk.CTkButton(results_frame, text="Save Results", font=("Arial", 14, "bold"), command=self.save_results)
        save_button.pack(pady=20)

    def update_results(self, revenue, prices, total_tickets, algorithm, duration, complexity, space, description):
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

    def save_results(self):
        try:
            revenue = int(self.result_entry.get().replace(",", ""))
            prices = self.prices_label.cget("text").split(": ")[1]
            tickets = int(self.tickets_label.cget("text").split(": ")[1])
            algorithm = self.algo_label.cget("text").split(": ")[1]
            self.app.db.save_result(
                timestamp=datetime.datetime.now(), revenue=revenue, prices=prices,
                tickets=tickets, algorithm=algorithm
            )
            # Assume self.app.history_tab exists
            # self.app.history_tab.refresh_history()
            self.app.sound_manager.play_sound("success")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
            self.app.sound_manager.play_sound("error")

# --- Main Window ---

class TicketRevenueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ticket Revenue Calculator")
        self.geometry("1200x800")
        self.db = Database()
        self.sound_manager = SoundManager()
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_calculator = self.tabview.add("Calculator")
        self.tab_results = self.tabview.add("Results")
        # self.tab_analytics = self.tabview.add("Analytics")
        # self.tab_history = self.tabview.add("History")
        # self.tab_settings = self.tabview.add("Settings")
        
        # Initialize tabs - Make sure ResultsTab is initialized
        self.calculator_tab = CalculatorTab(self.tab_calculator, self)
        self.results_tab = ResultsTab(self.tab_results, self) # ResultsTab needs to exist
        # self.analytics_tab = AnalyticsTab(self.tab_analytics, self)
        # self.history_tab = HistoryTab(self.tab_history, self)
        # self.settings_tab = SettingsTab(self.tab_settings, self)
        
        self.tabview.set("Calculator")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        try:
            if hasattr(self, 'db'):
                self.db.close()
            plt.close('all')
            self.destroy()
        except Exception as e:
            print(f"Error during closing: {e}")
            self.destroy()

# Placeholder classes for missing tabs (if needed)
# class AnalyticsTab:
#     def __init__(self, parent, app): pass
#     def update_analytics(self, prices, revenue): pass
#
# class HistoryTab:
#     def __init__(self, parent, app): pass
#     def refresh_history(self): pass
#
# class SettingsTab:
#     def __init__(self, parent, app): pass 