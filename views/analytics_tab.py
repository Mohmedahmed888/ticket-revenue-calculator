import customtkinter as ctk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
            # Get the *last* result for the analysis plots
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
            bg_color = '#FAFAFA' if mode == 'light' else '#2B2B2B' # Light/Dark background
            text_color = 'black' if mode == 'light' else 'white'
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
            total_tickets = sum(price_counts)

            # Calculate revenue contribution for each price
            revenue_per_price = [p * c for p, c in zip(unique_prices, price_counts)]
            total_revenue = sum(revenue_per_price)

            # Custom color palette that works well in both dark and light modes
            custom_colors = ['#4B89DC',  # Soft Blue
                            '#48CFAD',  # Mint
                            '#AC92EC',  # Lavender
                            '#FFCE54',  # Soft Yellow
                            '#FC6E51',  # Coral
                            '#ED5565']  # Soft Red

            # Ensure we have enough colors
            while len(custom_colors) < len(unique_prices):
                custom_colors.extend(custom_colors)
            colors = custom_colors[:len(unique_prices)]

            # Create the pie chart with improved styling
            wedges, texts, autotexts = self.ax1.pie(
                revenue_per_price,
                labels=[f"${p:,}" for p in unique_prices],
                autopct=lambda pct: f'{pct:.1f}%\n(${int(total_revenue * pct/100):,})',
                startangle=90,
                pctdistance=0.75,
                labeldistance=1.1,
                colors=colors,
                wedgeprops={'edgecolor': '#2B2B2B' if mode == 'dark' else '#FFFFFF', 
                            'linewidth': 1.5,
                            'alpha': 0.9}  # Slight transparency for better visibility
            )

            # Set background color based on mode
            bg_color = '#2B2B2B' if mode == 'dark' else '#FFFFFF'
            text_color = '#FFFFFF' if mode == 'dark' else '#2B2B2B'

            self.ax1.set_title(f'Revenue Distribution by Price\nTotal Revenue: ${total_revenue:,}', 
                               pad=20, fontsize=12, fontweight='bold',
                               color=text_color)

            # Improve text visibility and positioning
            for text in texts:
                text.set_color(text_color)
                text.set_fontsize(9)
                text.set_weight('bold')

            for autotext in autotexts:
                autotext.set_color(text_color)
                autotext.set_fontsize(8)
                autotext.set_weight('bold')

            # Add a legend with price, count, and revenue information
            legend_labels = [f"${p:,} ({c} tickets, ${p*c:,} revenue)" 
                            for p, c in zip(unique_prices, price_counts)]
            legend = self.ax1.legend(
                wedges, 
                legend_labels, 
                title="Price (Tickets, Revenue)",
                loc="center left",
                bbox_to_anchor=(1.1, 0.5),
                fontsize=9,
                title_fontsize=10
            )

            # Update legend colors
            legend.get_title().set_color(text_color)
            for text in legend.get_texts():
                text.set_color(text_color)

            # Set figure background color
            self.fig.patch.set_facecolor(bg_color)
            self.ax1.set_facecolor(bg_color)
            
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