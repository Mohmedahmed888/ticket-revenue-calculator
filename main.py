import customtkinter as ctk
import matplotlib.pyplot as plt
from views import TicketRevenueApp

def main():
    # Set initial appearance (can be overridden by settings loaded from DB in TicketRevenueApp)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run application
    app = TicketRevenueApp()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled application error: {e}")
        # Optionally show an error message box here too
        # from tkinter import messagebox
        # messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")
    finally:
        # Attempt to close any remaining plots on exit
        try:
            plt.close('all')
        except Exception:
            pass