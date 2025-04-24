import customtkinter as ctk
import matplotlib.pyplot as plt
from trk import TicketRevenueApp

def main():
    try:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        app = TicketRevenueApp()
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        try:
            # التأكد من إغلاق جميع النوافذ المتبقية
            plt.close('all')
        except:
            pass

if __name__ == "__main__":
    main()