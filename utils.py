import sqlite3
from datetime import datetime
import os
import winsound

# --- Database ---

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('ticket_revenue.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                revenue INTEGER,
                prices TEXT,
                tickets INTEGER,
                algorithm TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_name TEXT UNIQUE,
                setting_value TEXT
            )
        ''')
        self.conn.commit()
    
    def save_result(self, timestamp, revenue, prices, tickets, algorithm):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO results (timestamp, revenue, prices, tickets, algorithm)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, revenue, prices, tickets, algorithm))
        self.conn.commit()
    
    def get_results(self, limit=100):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timestamp, revenue, prices, tickets, algorithm
            FROM results
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def save_setting(self, name, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (setting_name, setting_value)
            VALUES (?, ?)
        ''', (name, value))
        self.conn.commit()
    
    def get_setting(self, name, default=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT setting_value
            FROM settings
            WHERE setting_name = ?
        ''', (name,))
        result = cursor.fetchone()
        return result[0] if result else default
    
    def close(self):
        if self.conn:
            self.conn.close()

# --- Sound Manager ---

class SoundManager:
    def __init__(self):
        self.sounds = {
            "success": "*",
            "error": "!"
        }
        self.enabled = os.environ.get('ENABLE_SOUNDS', 'true').lower() == 'true'
    
    def play_sound(self, sound_type):
        if not self.enabled:
            return
        try:
            if sound_type == "success":
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif sound_type == "error":
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except:
            pass
    
    def enable_sounds(self):
        self.enabled = True
        os.environ['ENABLE_SOUNDS'] = 'true'
    
    def disable_sounds(self):
        self.enabled = False
        os.environ['ENABLE_SOUNDS'] = 'false' 