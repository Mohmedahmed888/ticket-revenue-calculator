import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd

class HistoryTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.row_widgets = []
        self.create_widgets()
        self.load_history_data()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(main_frame, text="Calculation History", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 15))

        # --- Buttons --- 
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        button_style = {"font": ctk.CTkFont(size=13), "width": 120, "height": 32}
        refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", command=self.load_history_data, **button_style)
        refresh_btn.pack(side="left", padx=5)
        export_btn = ctk.CTkButton(btn_frame, text="Export Excel", command=self.export_to_excel, **button_style)
        export_btn.pack(side="left", padx=5)
        clear_btn = ctk.CTkButton(btn_frame, text="Clear History", command=self.clear_history, **button_style)
        clear_btn.pack(side="left", padx=5)

        # --- Table Container ---
        self.table_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=10)

        # --- Header Row --- 
        self.header_frame = ctk.CTkFrame(self.table_container, fg_color=self._get_header_color())
        self.header_frame.pack(fill="x", pady=(0, 1))

        # Column configuration with fixed widths
        self.column_config = {
            "Timestamp": {"width": 180, "weight": 3},
            "Revenue": {"width": 120, "weight": 2},
            "Method": {"width": 120, "weight": 2},
            "Tickets": {"width": 80, "weight": 1},
            "Duration (s)": {"width": 100, "weight": 1},
            "Prices Used": {"width": 200, "weight": 3}
        }

        # Create header cells
        for i, (col_name, config) in enumerate(self.column_config.items()):
            header_cell = ctk.CTkFrame(self.header_frame, fg_color="transparent", height=40)
            header_cell.grid(row=0, column=i, sticky="nsew", padx=1)
            header_cell.grid_propagate(False)
            
            label = ctk.CTkLabel(
                header_cell,
                text=col_name,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                anchor="center"
            )
            label.place(relx=0.5, rely=0.5, anchor="center")

        # Configure header frame columns
        for i, config in enumerate(self.column_config.values()):
            self.header_frame.grid_columnconfigure(i, weight=config["weight"], minsize=config["width"])

        # --- Scrollable Frame for Data Rows --- 
        self.scrollable_frame = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Configure scrollable frame columns
        for i, config in enumerate(self.column_config.values()):
            self.scrollable_frame.grid_columnconfigure(i, weight=config["weight"], minsize=config["width"])

        # Placeholder label
        self.no_data_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No historical records available.",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )

    def _get_row_colors(self):
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            return ("#2b2b2b", "#333333")
        else:
            return ("#f5f5f5", "#ffffff")

    def _get_header_color(self):
        mode = ctk.get_appearance_mode()
        return "#1f538d" if mode == "Dark" else "#2c7be5"
        
    def _get_text_color(self, element_type="data"):
        mode = ctk.get_appearance_mode()
        if element_type == "header":
            return "white"
        else:
            return "white" if mode == "Dark" else "black"

    def _clear_rows(self):
        """Clears existing data rows from the scrollable frame."""
        for widget in self.row_widgets:
            widget.destroy()
        self.row_widgets = []
        self.no_data_label.pack_forget() # Hide 'no data' label if it was visible

    def load_history_data(self):
        self._clear_rows()
        
        try:
            results = self.app.db.get_results()
            if not results:
                self.no_data_label.pack(pady=20)
                return

            even_color, odd_color = self._get_row_colors()
            text_color = self._get_text_color("data")

            for i, row in enumerate(results):
                row_frame = ctk.CTkFrame(
                    self.scrollable_frame,
                    fg_color=even_color if i % 2 == 0 else odd_color,
                    height=35
                )
                row_frame.pack(fill="x", pady=1)
                self.row_widgets.append(row_frame)

                # Configure row columns
                for col_idx, config in enumerate(self.column_config.values()):
                    row_frame.grid_columnconfigure(col_idx, weight=config["weight"], minsize=config["width"])

                try:
                    timestamp, prices, tickets, revenue, method, duration = row
                    
                    # Format the data
                    formatted_data = [
                        timestamp[:19],
                        f"{revenue:,}",
                        method.replace('_', ' ').title(),
                        str(tickets),
                        f"{duration:.2f}" if isinstance(duration, (int, float)) else "-",
                        str(prices) if prices is not None else ""
                    ]

                    # Create cells for each column
                    for col_idx, value in enumerate(formatted_data):
                        cell_frame = ctk.CTkFrame(row_frame, fg_color="transparent", height=35)
                        cell_frame.grid(row=0, column=col_idx, sticky="nsew", padx=1)
                        cell_frame.grid_propagate(False)
                        
                        label = ctk.CTkLabel(
                            cell_frame,
                            text=value,
                            font=ctk.CTkFont(size=11),
                            text_color=text_color,
                            anchor="center"
                        )
                        label.place(relx=0.5, rely=0.5, anchor="center")

                except Exception as fmt_e:
                    error_label = ctk.CTkLabel(
                        row_frame,
                        text=f"Error displaying row: {fmt_e}",
                        text_color="red",
                        anchor="w",
                        padx=5
                    )
                    error_label.grid(row=0, column=0, columnspan=6, sticky="ew")

        except Exception as e:
            messagebox.showerror("History Error", f"Failed to load history: {str(e)}")
            self.app.sound_manager.play_sound("error")
            self._clear_rows()
            self.no_data_label.configure(text=f"Error loading history: {e}", text_color="red")
            self.no_data_label.pack(pady=20)

    def export_to_excel(self):
        try:
            results = self.app.db.get_results(limit=10000) # Get all results for export
            if not results:
                messagebox.showwarning("No Data", "No records to export.")
                return

            # Ensure consistent column order/names with the database fetch
            df = pd.DataFrame(results, columns=["Timestamp", "Prices", "Tickets", "Revenue", "Method", "Duration"])
            # Reorder DF columns to match Treeview/Excel output preference if desired
            df = df[["Timestamp", "Revenue", "Method", "Tickets", "Duration", "Prices"]]

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
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all historical records?"):
            success = self.app.db.clear_all_history()
            if success:
                self.load_history_data() # Refresh display
                messagebox.showinfo("Deleted", "All history records deleted.")
                self.app.sound_manager.play_sound("success")
                # Optionally update analytics as well
                if hasattr(self.app, 'analytics_tab_instance'):
                    self.app.analytics_tab_instance.update_plot() # Refresh analytics plot 