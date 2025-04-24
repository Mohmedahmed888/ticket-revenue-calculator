import sqlite3
import datetime
import os
import winsound
from tkinter import messagebox, filedialog
import pandas as pd

# --- Database Class ---
class Database:
    def __init__(self, db_name='ticket_revenue.db'):
        """Initialize database connection and create tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(db_name)
            self.create_tables()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            self.conn = None

    def create_tables(self):
        """Create revenue_history table if it doesn't exist"""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    prices TEXT NOT NULL,
                    tickets INTEGER NOT NULL,
                    revenue INTEGER NOT NULL,
                    method TEXT NOT NULL,
                    duration REAL NOT NULL 
                )
            ''')
            # We can add the settings table here as well if needed from original trk.py,
            # but the original save/get_results used revenue_history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value TEXT
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to create tables: {str(e)}")

    def save_result(self, timestamp, prices_str, tickets, revenue, method, duration):
        """Save calculation result to the revenue_history table."""
        if not self.conn:
            print("DB Error: Attempted to save result with no connection.")
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO revenue_history 
                (date, prices, tickets, revenue, method, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                prices_str,
                tickets,
                revenue,
                method,
                duration
            ))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save result: {str(e)}")
            return False

    def get_results(self, limit=100):
        """Get recent calculation results from revenue_history table."""
        if not self.conn:
            print("DB Error: Attempted to get results with no connection.")
            return []
        try:
            cursor = self.conn.cursor()
            # Select all columns needed for history display
            cursor.execute("SELECT date, prices, tickets, revenue, method, duration FROM revenue_history ORDER BY date DESC LIMIT ?", (limit,))
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load history: {str(e)}")
            return []

    def clear_all_history(self):
        """Delete all records from the revenue_history table."""
        if not self.conn:
            print("DB Error: Attempted to clear history with no connection.")
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM revenue_history")
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete records: {str(e)}")
            return False
            
    def save_setting(self, name, value):
        """Save or update a setting in the settings table."""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (setting_name, setting_value)
                VALUES (?, ?)
            ''', (name, value))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save setting {name}: {str(e)}")

    def get_setting(self, name, default=None):
        """Get a setting value by name from the settings table."""
        if not self.conn:
            return default
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', (name,))
            result = cursor.fetchone()
            return result[0] if result else default
        except Exception as e:
            # Non-critical error, just return default
            print(f"Warning: Failed to get setting {name}: {str(e)}") 
            return default

    def close(self):
        """Close the database connection."""
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                 print(f"Error closing database: {str(e)}")
            finally:
                self.conn = None

# --- Sound Manager Class ---
class SoundManager:
    def __init__(self):
        """Initialize sound manager and load initial setting."""
        # Load setting from environment or default to True
        self.enabled = os.environ.get('ENABLE_SOUNDS', 'true').lower() == 'true' 
        # Or load from a persistent setting if Database class is available during init
        # Example: self.db = Database(); self.enabled = self.db.get_setting("sound_enabled", "True") == "True"
        # For simplicity now, using environment or default True.

    def play_sound(self, sound_type):
        """Play a system sound based on type if sounds are enabled."""
        if not self.enabled:
            return
        try:
            if sound_type == "success":
                # Use simple Beep from original code
                winsound.Beep(1000, 200) 
            elif sound_type == "error":
                winsound.Beep(500, 300)
            # Add other sound types if needed
        except Exception as e:
            # Silently fail if sound playback fails
            print(f"Sound playback error: {e}") 
            pass

    def enable_sounds(self, save_setting_func=None):
        """Enable sound effects and optionally save the setting."""
        self.enabled = True
        os.environ['ENABLE_SOUNDS'] = 'true' # Optional: reflect in env var
        if save_setting_func:
             save_setting_func("sound_enabled", "True")

    def disable_sounds(self, save_setting_func=None):
        """Disable sound effects and optionally save the setting."""
        self.enabled = False
        os.environ['ENABLE_SOUNDS'] = 'false' # Optional: reflect in env var
        if save_setting_func:
            save_setting_func("sound_enabled", "False")

    def toggle_sounds(self, current_state_bool, save_setting_func=None):
        """Toggle sounds based on the provided boolean state."""
        if current_state_bool:
            self.enable_sounds(save_setting_func)
        else:
            self.disable_sounds(save_setting_func) 