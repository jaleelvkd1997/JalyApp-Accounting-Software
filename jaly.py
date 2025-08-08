import customtkinter as ctk
from tkinter import messagebox
import jaly_main  # Import the main app

# Setup appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Create Login Window
login_app = ctk.CTk()
login_app.title("Login - Jaly")
login_app.geometry("350x300")


def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "1234":
        login_app.after(100, start_main_app)
        login_app.destroy()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")


def start_main_app():
    jaly_main.open_main_app()
    jaly_main.app.mainloop()


# UI Elements
ctk.CTkLabel(login_app, text="🔐 Login to Jaly", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

ctk.CTkLabel(login_app, text="Username:").pack()
username_entry = ctk.CTkEntry(login_app)
username_entry.pack(pady=5)

ctk.CTkLabel(login_app, text="Password:").pack()
password_entry = ctk.CTkEntry(login_app, show="*")
password_entry.pack(pady=5)

ctk.CTkButton(login_app, text="Login", command=login).pack(pady=20)

login_app.mainloop()