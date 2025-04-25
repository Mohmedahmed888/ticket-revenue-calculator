import customtkinter as ctk
from tkinter import messagebox

class CalculatorTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.price_entries = []
        self.entry_frames = []  # Store entry frames for deletion
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        input_title = ctk.CTkLabel(input_frame, text="Enter Ticket Prices", font=("Arial", 20, "bold"))
        input_title.pack(pady=10)
        
        # Frame for dynamic price entries
        self.entries_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        self.entries_frame.pack(fill="x", padx=20, pady=10)
        
        # Create initial entry
        self.add_price_entry()
        
        # # Add "Add Another Price" button
        # add_button = ctk.CTkButton(
        #     self.entries_frame, 
        #     text="+ Add Another Price", 
        #     font=ctk.CTkFont(size=13),
        #     height=35,
        #     command=self.add_price_entry
        # )
        # add_button.pack(fill="x", padx=5, pady=(10, 0))
        
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
        
        calculate_button = ctk.CTkButton(main_frame, text="Calculate Maximum Revenue ▶", font=("Arial", 18, "bold"), height=50, command=self.app.calculate_revenue)
        calculate_button.pack(pady=20)

    def add_price_entry(self):
        """Add a new price entry field to the entries frame."""
        entry_frame = ctk.CTkFrame(self.entries_frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=2)
        self.entry_frames.append(entry_frame)  # Store frame for deletion
        
        # Create a frame for the entry and delete button
        entry_control_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        entry_control_frame.pack(fill="x", expand=True)
        
        # Create the entry
        entry = ctk.CTkEntry(
            entry_control_frame, 
            placeholder_text=f"Price {len(self.price_entries) + 1}", 
            font=ctk.CTkFont(size=13), 
            height=35
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Create delete button
        delete_button = ctk.CTkButton(
            entry_control_frame,
            text="×",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#ff4444",
            hover_color="#cc0000",
            command=lambda f=entry_frame, e=entry: self.delete_price_entry(f, e)
        )
        delete_button.pack(side="right")
        
        # Bind the entry to add a new one when typing
        entry.bind('<Key>', lambda e, idx=len(self.price_entries): self.on_entry_type(e, idx))
        
        self.price_entries.append(entry)
        return entry

    def on_entry_type(self, event, entry_index):
        """Handle typing events on price entries to add new ones when needed."""
        # If this is the last entry and it's getting typed in, add a new one
        if entry_index == len(self.price_entries) - 1:
            self.add_price_entry()

    def delete_price_entry(self, frame, entry):
        """Delete a price entry field."""
        if len(self.price_entries) > 1:  # Don't delete if it's the last entry
            frame.destroy()
            self.price_entries.remove(entry)
            self.entry_frames.remove(frame)
            
            # Update placeholder text for remaining entries
            for i, remaining_entry in enumerate(self.price_entries, 1):
                remaining_entry.configure(placeholder_text=f"Price {i}")

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
        self.progress_frame.pack(fill="x", padx=20, pady=5)
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