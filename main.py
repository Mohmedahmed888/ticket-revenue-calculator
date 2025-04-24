import customtkinter as ctk
import matplotlib.pyplot as plt
from views import TicketRevenueApp

def main():
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run application
    app = TicketRevenueApp()
    app.mainloop()

if __name__ == "__main__":
    main()
    try:
        # Close all remaining windows
        plt.close('all')
    except:
        pass