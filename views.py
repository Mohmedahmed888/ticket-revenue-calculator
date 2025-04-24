import customtkinter as ctk
import datetime
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import os
from algorithms import brute_force_max_revenue, dynamic_programming_max_revenue, optimized_greedy_max_revenue
from utils import Database, SoundManager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

# --- Calculator Tab ---

class CalculatorTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
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
        
        # Progress bar frame (will be packed/unpacked in calculate_revenue)
        self.progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.set(0)
        # Don't pack progress_frame here initially
        
        calculate_button = ctk.CTkButton(main_frame, text="Calculate Maximum Revenue ▶", font=("Arial", 18, "bold"), height=50, command=self.app.calculate_revenue)
        calculate_button.pack(pady=20)
    
    def get_inputs(self):
        """Helper method to get and validate inputs from this tab."""
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
            elif total_tickets > 1000: # Limit from original code
                raise ValueError("Maximum number of tickets is 1000")
        except ValueError as e:
            if "Maximum number" in str(e):
                raise e
            raise ValueError("Please enter a valid number of tickets")
        
        if not prices:
            raise ValueError("Please enter at least one price")
        
        algorithm = self.algorithm_var.get()
        return prices, total_tickets, algorithm

    def show_progress(self):
        self.progress_frame.pack(fill="x", padx=20, pady=5) # Pack the frame first
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.start()

    def hide_progress(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_frame.pack_forget()

    def clear_fields(self):
        """Clear the input fields in the Calculator tab."""
        for entry in self.price_entries:
            entry.delete(0, "end")
        self.tickets_entry.delete(0, "end")
        # Optionally reset algorithm selection if needed
        # self.algorithm_var.set("brute_force")

# --- Results Tab ---

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
            
            print(f"Attempting to save: R={revenue}, P={prices_str}, T={tickets}, M={method}, D={duration}")
            success = self.app.db.save_result(
                timestamp=datetime.datetime.now(), 
                prices_str=prices_str,
                tickets=tickets, 
                revenue=revenue, 
                method=method, 
                duration=duration
            )
            
            if success:
                print("Save successful.")
                if hasattr(self.app, 'history_tab_instance'):
                    self.app.history_tab_instance.load_history_data()
                messagebox.showinfo("Success", "Result saved successfully!")
                self.app.sound_manager.play_sound("success")
            else:
                print("Save returned False, but no exception caught in DB method.")
                messagebox.showerror("Save Error", "Failed to save result. Database connection might be closed.")
                
        except Exception as e:
            print(f"Exception during save: {str(e)}")
            messagebox.showerror("Save Error", f"Failed to save result: {str(e)}")
            self.app.sound_manager.play_sound("error")

    def clear_results_display(self):
        """Clear the display fields in the Results tab AND input fields in Calculator tab."""
        # Clear Results Tab display
        self.main_result_entry.configure(state="normal")
        self.main_result_entry.delete(0, "end")
        self.main_result_entry.insert(0, "0")
        self.main_result_entry.configure(state="readonly")
        
        self.main_prices_label.configure(text="Prices: -")
        self.main_tickets_label.configure(text="Number of Tickets: -")
        self.main_algo_label.configure(text="Algorithm: -")
        self.main_time_label.configure(text="Time: -")
        self.main_time_complexity_label.configure(text="Time Complexity: -")
        self.main_space_complexity_label.configure(text="Space Complexity: -")
        self.main_steps_label.configure(text="-")
        
        # Clear Calculator Tab inputs by calling its clear_fields method
        if hasattr(self.app, 'calculator_tab_instance'):
             self.app.calculator_tab_instance.clear_fields()

# --- Analytics Tab ---

class AnalyticsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.fig = None
        self.canvas = None
        self.ax1 = None # Axis for pie chart
        self.ax2 = None # Axis for bar chart
        self.create_widgets()

    def create_widgets(self):
        self.analytics_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.analytics_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(self.analytics_frame, text="Revenue & Price Analytics", font=("Arial", 20, "bold"))
        title.pack(pady=(10, 20))

        # Frame for the plot (will hold the canvas)
        self.plot_frame = ctk.CTkFrame(self.analytics_frame)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Placeholder Label initially
        self.placeholder_label = ctk.CTkLabel(self.plot_frame, text="Analytics will be shown here after calculations.", text_color="gray")
        self.placeholder_label.pack(pady=50)

        # --- Buttons Frame --- 
        button_frame = ctk.CTkFrame(self.analytics_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10, padx=10)
        button_frame.grid_columnconfigure((0, 1), weight=1) # Center buttons

        refresh_button = ctk.CTkButton(button_frame, text="Refresh Plot", command=self.update_plot)
        refresh_button.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        save_button = ctk.CTkButton(button_frame, text="Save Chart", command=self.save_chart)
        save_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
    def update_plot(self):
        """Fetch data and update the plots to match trk.py functionality."""
        try:
            # Get the *last* result for the analysis plots (as in trk.py)
            # It seems the original `update_analytics` used the *current* prices/revenue passed to it,
            # not historical data. Let's adapt to use the *most recent* history entry for demonstration.
            # Or, ideally, it should be updated based on the *last successful calculation*. 
            # Let's retrieve the last successful calculation details from the ResultsTab.
            
            try:
                revenue_str = self.app.results_tab_instance.result_entry.get().replace(",", "")
                if not revenue_str or revenue_str == '0': 
                    self._display_placeholder("No recent calculation data available for analytics.")
                    return
                revenue = int(revenue_str)
                prices_str = self.app.results_tab_instance.prices_label.cget("text").replace("Prices: ", "")
                prices = [int(p.strip()) for p in prices_str.split(',') if p.strip().isdigit()]
                if not prices:
                    self._display_placeholder("Could not retrieve prices for analytics.")
                    return
            except Exception as e:
                self._display_placeholder(f"Error retrieving current results: {e}", error=True)
                return

            # --- Clear previous plot elements --- 
            if self.canvas:
                 self.canvas.get_tk_widget().destroy()
                 plt.close(self.fig) # Close the previous figure
            self.placeholder_label.pack_forget() # Hide placeholder
            self.plot_frame.configure(fg_color="transparent") 

            # --- Create new figure and subplots (axes) --- 
            self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5)) 
            
            # --- Configure colors based on theme --- 
            mode = ctk.get_appearance_mode().lower()
            bg_color = "#2b2b2b" if mode == "dark" else "#ebebeb"
            text_color = "white" if mode == "dark" else "black"
            self.fig.patch.set_facecolor(bg_color)
            self.ax1.set_facecolor(bg_color) 
            self.ax2.set_facecolor(bg_color)
            
            # Helper function to set text colors for axes
            def setup_ax_colors(ax):
                ax.tick_params(axis='x', colors=text_color)
                ax.tick_params(axis='y', colors=text_color)
                ax.spines['bottom'].set_color(text_color)
                ax.spines['left'].set_color(text_color)
                ax.spines['top'].set_color(bg_color)
                ax.spines['right'].set_color(bg_color)
                ax.yaxis.label.set_color(text_color)
                ax.xaxis.label.set_color(text_color)
                ax.title.set_color(text_color)

            setup_ax_colors(self.ax1)
            setup_ax_colors(self.ax2)

            # --- Plot 1: Price Distribution Pie Chart --- 
            unique_prices = sorted(list(set(prices)), reverse=True)
            price_counts = [prices.count(p) for p in unique_prices]
            pie_colors = plt.cm.Pastel1(np.linspace(0, 1, len(unique_prices))) 
            
            wedges, texts, autotexts = self.ax1.pie(price_counts, 
                       labels=[f"${p}" for p in unique_prices],
                       autopct='%1.1f%%',
                       colors=pie_colors,
                       textprops={'color': text_color}) 
            self.ax1.set_title('Price Distribution', pad=20, fontsize=12, fontweight='bold')
            # Improve text visibility
            for autotext in autotexts:
                autotext.set_color('black' if mode == 'light' else 'white') # Set contrast color
                autotext.set_weight('bold')
                autotext.set_fontsize(9)
                
            # --- Plot 2: Revenue Analysis Bar Chart --- 
            avg_price = sum(prices) / len(prices) if prices else 0
            max_price = max(prices) if prices else 0
            # Potential revenue calculation might need refinement based on logic
            # Using simple max_price * k as in original code
            tickets_str = self.app.results_tab_instance.tickets_label.cget("text").replace("Number of Tickets: ", "")
            k = int(tickets_str) if tickets_str.isdigit() else len(prices) # Fallback k
            potential_revenue = max_price * k # Based on original calculation
            
            categories = ['Average\nPrice', 'Highest\nPrice', 'Achieved\nRevenue', 'Max Potential\n(MaxPx * k)']
            values = [avg_price, max_price, revenue, potential_revenue]
            bar_colors = ['#3498DB', '#E74C3C', '#2ECC71', '#95A5A6']
            
            bars = self.ax2.bar(categories, values, color=bar_colors)
            self.ax2.set_title('Revenue Analysis', pad=20, fontsize=12, fontweight='bold')
            
            for bar in bars:
                height = bar.get_height()
                self.ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom', color=text_color, fontsize=9)
            
            self.ax2.grid(True, axis='y', linestyle='--', alpha=0.3)
            self.ax2.set_ylabel('Value ($)', fontsize=10)
            self.ax2.tick_params(axis='x', rotation=0)
            
            # --- Final adjustments and embedding --- 
            plt.tight_layout(pad=3.0)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.draw() 
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Analytics Error", f"Failed to update analytics: {str(e)}")
            self.app.sound_manager.play_sound("error")
            self._display_placeholder(f"Error generating plot: {e}", error=True)

    def _display_placeholder(self, text, error=False):
        """Helper to show a message when plot cannot be displayed."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.fig)
            self.canvas = None
            self.fig = None
        self.placeholder_label.configure(text=text, text_color="red" if error else "gray")
        self.placeholder_label.pack(pady=50) # Make sure it's visible
        self.plot_frame.configure(fg_color="transparent")
        
    def save_chart(self):
        if not self.fig:
            messagebox.showwarning("Save Error", "No chart available to save.")
            return
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                title="Save Chart As"
            )
            if not file_path:
                return # User cancelled
            
            self.fig.savefig(file_path)
            messagebox.showinfo("Success", f"Chart saved successfully to\n{file_path}")
            self.app.sound_manager.play_sound("success")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save chart: {str(e)}")
            self.app.sound_manager.play_sound("error")

# --- History Tab ---

class HistoryTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        self.load_history_data() # Load initial history

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(main_frame, text="Calculation History", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 20))

        # Frame for buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        button_style = {"font": ctk.CTkFont(size=13), "width": 120, "height": 32}
        refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", command=self.load_history_data, **button_style)
        refresh_btn.pack(side="left", padx=5)
        export_btn = ctk.CTkButton(btn_frame, text="Export Excel", command=self.export_to_excel, **button_style)
        export_btn.pack(side="left", padx=5)
        clear_btn = ctk.CTkButton(btn_frame, text="Clear History", command=self.clear_history, **button_style)
        clear_btn.pack(side="left", padx=5)

        # Use CTkTextbox for history display (as in previous version)
        self.history_textbox = ctk.CTkTextbox(main_frame, font=("Courier New", 12), wrap="none")
        self.history_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.history_textbox.configure(state="disabled") # Make read-only

    def load_history_data(self):
        """Load data from DB and display in the Textbox."""
        print("Attempting to load history...")
        try:
            results = self.app.db.get_results()
            print(f"Fetched {len(results)} records from DB.")
            
            self.history_textbox.configure(state="normal")
            self.history_textbox.delete("1.0", "end")

            if not results:
                self.history_textbox.insert("1.0", "No historical records available.")
                print("No records found or returned from DB.")
            else:
                header = f"{"Timestamp":<22} {"Revenue":>15} {"Method":<20} {"Tickets":>8} {"Duration":>10} {"Prices"}\n"
                separator = "-" * 110 + "\n"
                self.history_textbox.insert("end", header)
                self.history_textbox.insert("end", separator)

                for i, row in enumerate(results):
                    try:
                        timestamp, prices, tickets, revenue, method, duration = row
                        formatted_ts = timestamp[:19]
                        formatted_revenue = f"{revenue:,}"
                        formatted_duration = f"{duration:.2f}s"
                        line = f"{formatted_ts:<22} {formatted_revenue:>15} {method.replace('_', ' ').title():<20} {tickets:>8} {formatted_duration:>10} {prices}\n"
                        self.history_textbox.insert("end", line)
                    except Exception as fmt_e:
                        print(f"Error formatting/inserting row {i}: {row} -> {fmt_e}")
                        self.history_textbox.insert("end", f"Error displaying record: {row}\n")

            self.history_textbox.configure(state="disabled")
            print("History load complete.")
        except Exception as e:
            print(f"Exception during history load: {str(e)}")
            messagebox.showerror("History Error", f"Failed to load history: {str(e)}")
            self.app.sound_manager.play_sound("error")
            try:
                self.history_textbox.configure(state="normal")
                self.history_textbox.delete("1.0", "end")
                self.history_textbox.insert("1.0", f"Error loading history: {e}")
                self.history_textbox.configure(state="disabled")
            except: pass

    def export_to_excel(self):
        """Export history data to an Excel file."""
        try:
            results = self.app.db.get_results(limit=10000) # Get all results for export
            if not results:
                messagebox.showwarning("No Data", "No records to export.")
                return

            df = pd.DataFrame(results, columns=["Date", "Prices", "Tickets", "Revenue", "Method", "Duration"])
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save History As"
            )

            if not file_path:
                return # User cancelled

            df.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"History exported to {file_path}")
            self.app.sound_manager.play_sound("success")
        except Exception as e:
            messagebox.showerror("Export Error", f"Export failed: {str(e)}")
            self.app.sound_manager.play_sound("error")

    def clear_history(self):
        """Clear all records from the history database."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all historical records?"):           
            success = self.app.db.clear_all_history()
            if success:
                self.load_history_data() # Refresh display
                messagebox.showinfo("Deleted", "All history records deleted.")
                self.app.sound_manager.play_sound("success")
                # Optionally update analytics as well
                if hasattr(self.app, 'analytics_tab_instance'):
                    self.app.analytics_tab_instance.update_plot()
            # Error messages are handled within db.clear_all_history

# --- Settings Tab ---

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
        
# --- Main Application Class --- (Based on trk.py)
class TicketRevenueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
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
        # Cleanup binding (less critical now with on_closing)
        # self.bind("<Destroy>", self.cleanup) 
        
        # Initial history load is now handled within HistoryTab.__init__

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

    # Note: The cleanup method bound to <Destroy> might be redundant 
    # if on_closing handles everything reliably. Removed its binding for now.
    # def cleanup(self, event=None): ... 

    # Note: Methods like save_result, clear_fields, load_history_data, export_to_excel,
    # clear_history, update_analytics, save_chart, change_appearance_mode are now 
    # part of their respective Tab classes (ResultsTab, HistoryTab, AnalyticsTab, SettingsTab)
    # and are called via the instances (e.g., self.results_tab_instance.save_current_results()).
    # The main calculate_revenue method orchestrates the process. 