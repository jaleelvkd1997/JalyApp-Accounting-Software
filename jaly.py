import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import datetime

# Set appearance
ctk.set_appearance_mode("light")  # or "dark"
ctk.set_default_color_theme("blue")  # also: "green", "dark-blue"

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
    t_type = type_option.get()
    t_amount = amount_entry.get()
    t_desc = desc_entry.get()

    if not t_date or not t_type or not t_amount:
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return

    try:
        float(t_amount)
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

    date_entry.delete(0, ctk.END)
    amount_entry.delete(0, ctk.END)
    desc_entry.delete(0, ctk.END)
    type_option.set("")

# ----------- View Transactions -----------
def view_transactions():
    view_win = ctk.CTkToplevel(app)
    view_win.title("All Transactions")
    view_win.geometry("700x400")

    # Treeview with scrollbar
    import tkinter.ttk as ttk  # only for Treeview
    import tkinter as tk  # only for scrollbar

    cols = ("ID", "Date", "Type", "Amount", "Description")
    tree = ttk.Treeview(view_win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(view_win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Get data from DB
    conn = sqlite3.connect("jaly_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", "end", values=row)

# ----------- App Window -----------
app = ctk.CTk()
app.title("Jaly Accounting Software")
app.geometry("500x600")

# Title
title = ctk.CTkLabel(app, text="💼 Jaly Accounting", font=ctk.CTkFont(size=22, weight="bold"))
title.pack(pady=20)

# Date
date_label = ctk.CTkLabel(app, text="Date (YYYY-MM-DD):")
date_label.pack()
date_entry = ctk.CTkEntry(app)
date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
date_entry.pack(pady=5)

# Type
type_label = ctk.CTkLabel(app, text="Type:")
type_label.pack()
type_option = ctk.CTkOptionMenu(app, values=["Income", "Expense"])
type_option.pack(pady=5)

# Amount
amount_label = ctk.CTkLabel(app, text="Amount:")
amount_label.pack()
amount_entry = ctk.CTkEntry(app)
amount_entry.pack(pady=5)

# Description
desc_label = ctk.CTkLabel(app, text="Description:")
desc_label.pack()
desc_entry = ctk.CTkEntry(app)
desc_entry.pack(pady=5)

# Save Button
save_btn = ctk.CTkButton(app, text="💾 Save Transaction", command=save_transaction)
save_btn.pack(pady=15)

# View Button
view_btn = ctk.CTkButton(app, text="📄 View Transactions", command=view_transactions)
view_btn.pack(pady=5)

# Initialize DB
create_table()

# Run App
app.mainloop()