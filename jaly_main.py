import os
import customtkinter as ctk
import csv
import sqlite3
import datetime
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import tkinter as tk
from PIL import Image

class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

# --- Force working directory to script folder (safe) ---
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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

# ---------- Globals for widgets / vars ----------
app = None
date_entry = None
type_option = None
amount_entry = None
desc_entry = None
income_var = None
expense_var = None
balance_var = None

# ---------- Utility: calculate summary ----------
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

# ---------- Save transaction ----------
def save_transaction():
    global date_entry, type_option, amount_entry, desc_entry
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
    cursor.execute(
        "INSERT INTO transactions (date, type, amount, description) VALUES (?, ?, ?, ?)",
        (t_date, t_type, t_amount, t_desc)
    )
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

# ---------- View transactions (Toplevel) ----------
def view_transactions():
    view_win = ctk.CTkToplevel(app)
    view_win.title("All Transactions")
    view_win.geometry("900x600")

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
        tree.column(col, anchor="center", width=140)
    tree.pack(side="left", fill="both", expand=True, padx=(10,0))

    scrollbar = tk.Scrollbar(view_win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y", padx=(0,10))

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

# ---------- Export data ----------
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

# ---------- Page rendering helpers ----------
def clear_main_frame(main_frame):
    for w in main_frame.winfo_children():
        w.destroy()

def show_home(main_frame):
    clear_main_frame(main_frame)

    # Summary Frame
    summary_frame = ctk.CTkFrame(main_frame)
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

    # Transaction entry area
    entry_frame = ctk.CTkFrame(main_frame)
    entry_frame.pack(pady=10, padx=10, fill="x")

    # Date input
    ctk.CTkLabel(entry_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    global date_entry, type_option, amount_entry, desc_entry
    date_entry = ctk.CTkEntry(entry_frame, width=160)
    date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    date_entry.grid(row=0, column=1, padx=5, pady=5)

    # Type
    ctk.CTkLabel(entry_frame, text="Type:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    type_option = ctk.CTkOptionMenu(entry_frame, values=["Income", "Expense"], width=120)
    type_option.grid(row=0, column=3, padx=5, pady=5)

    # Amount
    ctk.CTkLabel(entry_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    amount_entry = ctk.CTkEntry(entry_frame, width=160)
    amount_entry.grid(row=1, column=1, padx=5, pady=5)

    # Description
    ctk.CTkLabel(entry_frame, text="Description:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
    desc_entry = ctk.CTkEntry(entry_frame, width=300)
    desc_entry.grid(row=1, column=3, padx=5, pady=5)

    # Buttons
    btn_frame = ctk.CTkFrame(main_frame)
    btn_frame.pack(pady=10)
    ctk.CTkButton(btn_frame, text="💾 Save Transaction", command=save_transaction).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="📄 View Transactions", command=view_transactions).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="📤 Export All to CSV", command=export_data).pack(side="left", padx=10)

def show_reports(main_frame):
    clear_main_frame(main_frame)
    ctk.CTkLabel(main_frame, text="Reports", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
    ctk.CTkLabel(main_frame, text="(Reports & charts will be added here.)").pack(pady=10)

def show_settings(main_frame):
    clear_main_frame(main_frame)
    ctk.CTkLabel(main_frame, text="Settings", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
    ctk.CTkLabel(main_frame, text="(Settings and user preferences.)").pack(pady=10)

def do_logout():
    # A simple logout that closes the main app window.
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        app.destroy()

# ---------- Main Application Window ----------
def open_main_app():
    global app, income_var, expense_var, balance_var

    app = ctk.CTk()
    app.title("Jaly Accounting Software")
    app.geometry("1200x700")

    # configure grid: sidebar | main area
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)

    # Sidebar
    sidebar = ctk.CTkFrame(app, width=260, corner_radius=0)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_rowconfigure(6, weight=1)  # push logout to bottom

    # --- Load and show logo in sidebar ---
    try:
        logo_path = os.path.join(script_dir, "logo.png")
        logo_image = ctk.CTkImage(light_image=Image.open(logo_path), size=(90, 90))
        ctk.CTkLabel(sidebar, image=logo_image, text="").pack(pady=(20, 6))
    except Exception as e:
        # if anything goes wrong just show text instead of breaking UI
        print("⚠️ Couldn't load logo in main window:", e)
        ctk.CTkLabel(sidebar, text="Jaly", font=ctk.CTkFont(size=18)).pack(pady=(20,6))

    ctk.CTkLabel(sidebar, text="Jaly Accounting", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0,20))

    # Sidebar buttons
    # We'll create the main_frame first and pass it into handlers using lambda
    main_frame = ctk.CTkFrame(app, corner_radius=8)
    main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    ctk.CTkButton(sidebar, text="🏠 Home", width=220, command=lambda: show_home(main_frame)).pack(pady=6)
    ctk.CTkButton(sidebar, text="📊 Reports", width=220, command=lambda: show_reports(main_frame)).pack(pady=6)
    ctk.CTkButton(sidebar, text="⚙ Settings", width=220, command=lambda: show_settings(main_frame)).pack(pady=6)

    # Logout button at bottom
    logout_btn = ctk.CTkButton(sidebar, text="🚪 Logout", fg_color="red", hover_color="#cc0000", width=220, command=do_logout)
    logout_btn.pack(side="bottom", pady=20)

    # Initialize StringVars AFTER the app is created
    income_var = ctk.StringVar(value="₹ 0.00")
    expense_var = ctk.StringVar(value="₹ 0.00")
    balance_var = ctk.StringVar(value="₹ 0.00")

    # Show default page
    show_home(main_frame)
    calculate_summary()

    app.mainloop()

# ---------- Run if main ----------
if __name__ == "__main__":
    create_table()
    open_main_app()