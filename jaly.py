import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import jaly_main  # Import your main app

# --- Force working directory to script folder ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Setup appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Create Login Window
login_app = ctk.CTk()
login_app.title("Login - Jaly")
login_app.geometry("1200x700")

# --- Load and show logo ---
try:
    logo_image = ctk.CTkImage(
        light_image=Image.open("logo.png"),
        size=(100, 100)
    )
    ctk.CTkLabel(login_app, image=logo_image, text="").pack(pady=(20, 5))
except FileNotFoundError:
    print("⚠️ Logo file not found: logo.png")

def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "1234":
        login_app.quit()
        login_app.destroy()
        jaly_main.create_table()
        jaly_main.open_main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Title
ctk.CTkLabel(login_app, text="🔐 Login to Jaly", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

# Username
ctk.CTkLabel(login_app, text="Username:").pack()
username_entry = ctk.CTkEntry(login_app)
username_entry.pack(pady=5)

# Password
ctk.CTkLabel(login_app, text="Password:").pack()
password_entry = ctk.CTkEntry(login_app, show="*")
password_entry.pack(pady=5)

# Login Button
ctk.CTkButton(login_app, text="Login", command=login).pack(pady=20)

login_app.mainloop()