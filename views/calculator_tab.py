import customtkinter as ctk

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