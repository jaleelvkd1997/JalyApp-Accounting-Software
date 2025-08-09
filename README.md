Install Python on Your Windows PC Go to https://www.python.org/downloads/
Download the latest Python for Windows
Run the installer and make sure you check this box: ✅ Add Python to PATH
Click Install Now
After install, open Command Prompt and type:
python --version

install VS Code

Step 1: Create Your First "Jaly" Window
import tkinter as tk
window
# Title label
title 
# Just a placeholder message
message

Step 2: Add Transaction with database
Store it in a database (SQLite – very easy and built into Python)
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
# ----------- Database Setup -----------
def create_table():

Step 3 — View All Transactions
Use Treeview from tkinter.ttk to show table with rows and columns
 Step 3.5: Make the UI Prettier Using CustomTkinter
pip install customtkinter


Save the logo
Save the file you just got as logo.png (keep it a PNG for transparency).

Place it in the same folder as jaly.py and jaly_main.py.

Step 2 – Install Pillow (if not already)
This library lets us use the image in CustomTkinter:


pip install pillow
pip install matplotlib


MAking exe file
pip install pyinstaller
From your project folder (where your jaly.py or jaly_main.py is), run:
pyinstaller --noconsole --onefile --icon=logo.ico jaly.py
