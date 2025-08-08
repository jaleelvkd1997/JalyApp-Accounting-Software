import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

# ----------- Database Setup -----------
def create_table():
    conn = sqlite3.connect("jaly_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            amount REAL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

# ----------- Save Transaction -----------
def save_transaction():
    t_date = date_entry.get()
    t_type = type_combobox.get()
    t_amount = amount_entry.get()
    t_desc = desc_entry.get()

    # Validate input
    if not t_date or not t_type or not t_amount:
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return

    try:
        float(t_amount)  # check amount is number
    except:
        messagebox.showerror("Invalid", "Amount must be a number.")
        return

    conn = sqlite3.connect("jaly_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (date, type, amount, description) VALUES (?, ?, ?, ?)",
                   (t_date, t_type, t_amount, t_desc))
    conn.commit()
    conn.close()
    messagebox.showinfo("Saved", "Transaction saved successfully!")

    # Clear inputs
    date_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    type_combobox.set("")

# ----------- UI Setup -----------
window = tk.Tk()
window.title("Jaly Accounting Software")
window.geometry("500x500")
window.config(bg="#f8f8f8")

title = tk.Label(window, text="Add Transaction", font=("Arial", 16, "bold"), bg="#f8f8f8")
title.pack(pady=20)

# Date
date_label = tk.Label(window, text="Date (YYYY-MM-DD):", bg="#f8f8f8")
date_label.pack()
date_entry = tk.Entry(window)
date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))  # default today's date
date_entry.pack(pady=5)

# Type
type_label = tk.Label(window, text="Type:", bg="#f8f8f8")
type_label.pack()
type_combobox = ttk.Combobox(window, values=["Income", "Expense"])
type_combobox.pack(pady=5)

# Amount
amount_label = tk.Label(window, text="Amount:", bg="#f8f8f8")
amount_label.pack()
amount_entry = tk.Entry(window)
amount_entry.pack(pady=5)

# Description
desc_label = tk.Label(window, text="Description:", bg="#f8f8f8")
desc_label.pack()
desc_entry = tk.Entry(window)
desc_entry.pack(pady=5)

# Save Button
save_button = tk.Button(window, text="Save Transaction", command=save_transaction, bg="#4CAF50", fg="white", padx=10, pady=5)
save_button.pack(pady=20)

# Run DB Setup
create_table()

# Start the app
window.mainloop()