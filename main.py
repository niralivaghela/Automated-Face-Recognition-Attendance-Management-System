"""
Face Detection Attendance System
Main Entry Point
"""
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from login import LoginWindow


def check_dependencies():
    required = ['cv2', 'PIL', 'mysql.connector', 'pandas', 'numpy']
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return missing


if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    db.initialize_database()

    # ── Start background scheduler ────────────────────
    try:
        from auto_scheduler import AttendanceScheduler
        scheduler = AttendanceScheduler(db)
        scheduler.start()
        print("[✅] Auto-Scheduler started")
    except Exception as e:
        print(f"[⚠️] Scheduler not started: {e}")
        scheduler = None

    # Start login window
    root = tk.Tk()
    app = LoginWindow(root)

    def on_close():
        if scheduler: 
            scheduler.stop()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()