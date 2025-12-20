import tkinter as tk
from tkinter import messagebox
import auth


def login():
    pwd = password_entry.get()

    if not pwd:
        messagebox.showerror("Error", "Password required")
        return

    try:
        if auth.master_exists():
            if auth.verify_master(pwd):
                messagebox.showinfo("Success", "Login successful")
                root.destroy()
            else:
                messagebox.showerror("Error", "Incorrect password")
        else:
            auth.create_master(pwd)
            messagebox.showinfo("Success", "Master password created")
            root.destroy()

    except Exception as e:
        messagebox.showerror("Error", str(e))


root = tk.Tk()
root.title("CipherVault Login")
root.geometry("300x180")

tk.Label(root, text="Master Password").pack(pady=10)

password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=login).pack(pady=15)

root.mainloop()
