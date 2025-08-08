import customtkinter as ctk
import csv
from tkinter import filedialog, messagebox
import sqlite3
import datetime
import tkinter.ttk as ttk
import tkinter as tk

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

# ----------- Calculate Summary -----------
def calculate_summary():
    conn = sqlite3.connect("jaly_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT type, amount FROM transactions")
    rows = cursor.fetchall()
    conn.close()

    total_income = sum(float(row[1]) for row in rows if row[0] == "Income")
    total_expense = sum(float(row[1]) for row in rows if row[0] == "Expense")
    balance = total_income - total_expense

    income_var.set(f"₹ {total_income:.2f}")
    expense_var.set(f"₹ {total_expense:.2f}")
    balance_var.set(f"₹ {balance:.2f}")

# ----------- Save Transaction -----------
def save_transaction():
    t_date = date_entry.get()
    t_type = type_option.get()
    t_amount = amount_entry.get()
    t_desc = desc_entry.get()

    if not t_date or not t_type or not t_amount:
        messagebox.showwarning("Missing Info", "Please fill in all required fields.")
        return

    try:
        float(t_amount)
    except ValueError:
        messagebox.showerror("Invalid", "Amount must be a number.")
        return

    conn = sqlite3.connect("jaly_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (date, type, amount, description) VALUES (?, ?, ?, ?)",
                   (t_date, t_type, t_amount, t_desc))
    conn.commit()
    conn.close()
    messagebox.showinfo("Saved", "Transaction saved successfully!")
    calculate_summary()

    # Clear inputs
    date_entry.delete(0, ctk.END)
    date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    amount_entry.delete(0, ctk.END)
    desc_entry.delete(0, ctk.END)
    type_option.set("")

# ----------- View Transactions -----------
def view_transactions():
    view_win = ctk.CTkToplevel(app)
    view_win.title("All Transactions")
    view_win.geometry("750x500")

    # Filter Frame
    filter_frame = ctk.CTkFrame(view_win)
    filter_frame.pack(pady=10, padx=10, fill="x")

    # Type Filter
    type_label = ctk.CTkLabel(filter_frame, text="Type:")
    type_label.grid(row=0, column=0, padx=5, pady=5)
    filter_type = ctk.CTkOptionMenu(filter_frame, values=["All", "Income", "Expense"])
    filter_type.set("All")
    filter_type.grid(row=0, column=1, padx=5, pady=5)

    # Start Date
    start_label = ctk.CTkLabel(filter_frame, text="Start Date (YYYY-MM-DD):")
    start_label.grid(row=0, column=2, padx=5, pady=5)
    start_date = ctk.CTkEntry(filter_frame, width=120)
    start_date.grid(row=0, column=3, padx=5, pady=5)

    # End Date
    end_label = ctk.CTkLabel(filter_frame, text="End Date (YYYY-MM-DD):")
    end_label.grid(row=0, column=4, padx=5, pady=5)
    end_date = ctk.CTkEntry(filter_frame, width=120)
    end_date.grid(row=0, column=5, padx=5, pady=5)

    # Treeview Table
    cols = ("ID", "Date", "Type", "Amount", "Description")
    tree = ttk.Treeview(view_win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(view_win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def load_filtered_data():
        type_value = filter_type.get()
        start = start_date.get()
        end = end_date.get()

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if type_value != "All":
            query += " AND type = ?"
            params.append(type_value)

        if start:
            query += " AND date >= ?"
            params.append(start)

        if end:
            query += " AND date <= ?"
            params.append(end)

        conn = sqlite3.connect("jaly_data.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Clear existing rows
        for i in tree.get_children():
            tree.delete(i)

        for row in rows:
            tree.insert("", "end", values=row)

    filter_btn = ctk.CTkButton(filter_frame, text="Apply Filter", command=load_filtered_data)
    filter_btn.grid(row=0, column=6, padx=10)

    # Load all data initially
    load_filtered_data()

# ----------- Export Data -----------
def export_data():
    conn = sqlite3.connect("jaly_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        messagebox.showinfo("No Data", "No transactions to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save As"
    )

    if not file_path:
        return

    with open(file_path, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Date", "Type", "Amount", "Description"])
        writer.writerows(rows)

    messagebox.showinfo("Exported", f"Transactions exported to:\n{file_path}")

# ----------- Main Application Window -----------
def open_main_app():
    global app
    global date_entry, type_option, amount_entry, desc_entry
    global income_var, expense_var, balance_var

    app = ctk.CTk()
    app.title("Jaly Accounting Software")
    app.geometry("500x600")

    # Create StringVars AFTER app is created
    income_var = ctk.StringVar(value="₹ 0.00")
    expense_var = ctk.StringVar(value="₹ 0.00")
    balance_var = ctk.StringVar(value="₹ 0.00")

    # Title
    title = ctk.CTkLabel(app, text="💼 Jaly Accounting", font=ctk.CTkFont(size=22, weight="bold"))
    title.pack(pady=20)

    # Summary Frame
    summary_frame = ctk.CTkFrame(app)
    summary_frame.pack(pady=10, padx=10, fill="x")

    # Labels for summary
    income_label = ctk.CTkLabel(summary_frame, text="Income:", font=ctk.CTkFont(size=14))
    income_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    income_value = ctk.CTkLabel(summary_frame, textvariable=income_var, text_color="green")
    income_value.grid(row=0, column=1, padx=10, pady=5)

    expense_label = ctk.CTkLabel(summary_frame, text="Expense:", font=ctk.CTkFont(size=14))
    expense_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    expense_value = ctk.CTkLabel(summary_frame, textvariable=expense_var, text_color="red")
    expense_value.grid(row=1, column=1, padx=10, pady=5)

    balance_label = ctk.CTkLabel(summary_frame, text="Balance:", font=ctk.CTkFont(size=14, weight="bold"))
    balance_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    balance_value = ctk.CTkLabel(summary_frame, textvariable=balance_var, text_color="blue")
    balance_value.grid(row=2, column=1, padx=10, pady=5)

    # Date input
    ctk.CTkLabel(app, text="Date (YYYY-MM-DD):").pack()
    date_entry = ctk.CTkEntry(app)
    date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    date_entry.pack(pady=5)

    # Type input
    ctk.CTkLabel(app, text="Type:").pack()
    type_option = ctk.CTkOptionMenu(app, values=["Income", "Expense"])
    type_option.pack(pady=5)

    # Amount input
    ctk.CTkLabel(app, text="Amount:").pack()
    amount_entry = ctk.CTkEntry(app)
    amount_entry.pack(pady=5)

    # Description input
    ctk.CTkLabel(app, text="Description:").pack()
    desc_entry = ctk.CTkEntry(app)
    desc_entry.pack(pady=5)

    # Buttons
    ctk.CTkButton(app, text="💾 Save Transaction", command=save_transaction).pack(pady=10)
    ctk.CTkButton(app, text="📄 View Transactions", command=view_transactions).pack(pady=5)
    ctk.CTkButton(app, text="📤 Export All to CSV", command=export_data).pack(pady=5)

    # Initial summary calculation
    calculate_summary()

    app.mainloop()

# ----------- Run if Main -----------
if __name__ == "__main__":
    create_table()
    open_main_app()