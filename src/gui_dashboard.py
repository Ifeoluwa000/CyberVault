import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from cryptography.fernet import Fernet
from crypto_utils import generate_key
import vault
import auth
import re
import random
import string

# -------------------------------
# Password Strength Checker
# -------------------------------
def password_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1

    if score <= 2:
        msg = "Weak"
    elif score in [3, 4]:
        msg = "Medium"
    else:
        msg = "Strong"

    return score, msg

# -------------------------------
# Strong Password Generator
# -------------------------------
def generate_strong_password(length=12):
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = "".join(random.choice(all_chars) for _ in range(length))
    return password

# -------------------------------
# Master Password Login
# -------------------------------
master_password = simpledialog.askstring(
    "Master Password",
    "Enter Master Password:",
    show="*"
)

if not master_password:
    messagebox.showerror("Error", "Master password required")
    exit()

if not auth.verify_master(master_password):
    messagebox.showerror("Error", "Incorrect master password")
    exit()

# -------------------------------
# Setup Encryption
# -------------------------------
key = generate_key(master_password)
fernet = Fernet(key)
vault_data = vault.load_vault(fernet)

# -------------------------------
# Main Window
# -------------------------------
root = tk.Tk()
root.title("CipherVault Dashboard")
root.geometry("550x450")

# Treeview for accounts
account_tree = ttk.Treeview(root, columns=("Account", "Strength"), show="headings")
account_tree.heading("Account", text="Account")
account_tree.heading("Strength", text="Strength")
account_tree.pack(pady=20, fill=tk.X)

# Color tag configuration
account_tree.tag_configure("Weak", foreground="red")
account_tree.tag_configure("Medium", foreground="orange")
account_tree.tag_configure("Strong", foreground="green")

# -------------------------------
# Functions
# -------------------------------
def refresh_list():
    for i in account_tree.get_children():
        account_tree.delete(i)
    for account, data in vault_data.items():
        _, strength = password_strength(data["password"])
        account_tree.insert("", "end", values=(account, strength), tags=(strength,))

def add_account():
    popup = tk.Toplevel(root)
    popup.title("Add Account")
    popup.geometry("300x200")
    popup.grab_set()  # Make it modal

    tk.Label(popup, text="Account Name:").pack(pady=5)
    entry_name = tk.Entry(popup)
    entry_name.pack()

    tk.Label(popup, text="Username/Email:").pack(pady=5)
    entry_username = tk.Entry(popup)
    entry_username.pack()

    tk.Label(popup, text="Password:").pack(pady=5)
    entry_password = tk.Entry(popup, show="*")
    entry_password.pack()

    def submit():
        name = entry_name.get().strip()
        username = entry_username.get().strip()
        password = entry_password.get().strip()

        if not (name and username and password):
            messagebox.showerror("Error", "All fields are required", parent=popup)
            return

        # Password strength check
        score, strength = password_strength(password)
        if strength == "Weak":
            proceed = messagebox.askyesno(
                "Weak Password",
                "This password is weak.\nDo you want a recommended strong password?",
                parent=popup
            )
            if proceed:
                password = generate_strong_password()
                messagebox.showinfo("Recommended Password", f"Use this password: {password}", parent=popup)
                accept = messagebox.askyesno(
                    "Use Suggested Password?",
                    "Do you want to use the suggested password?",
                    parent=popup
                )
                if not accept:
                    return  # Let user edit manually

        vault_data[name] = {"username": username, "password": password}
        vault.save_vault(vault_data, fernet)
        refresh_list()
        messagebox.showinfo("Success", f"{name} added! Password strength: {strength}", parent=popup)
        popup.destroy()

    tk.Button(popup, text="Submit", command=submit).pack(pady=10)


def view_account():
    selected = account_tree.selection()
    if not selected:
        messagebox.showerror("Error", "No account selected")
        return
    name = account_tree.item(selected[0])["values"][0]
    data = vault_data[name]
    messagebox.showinfo(
        name,
        f"Username: {data['username']}\nPassword: {data['password']}"
    )

def delete_account():
    selected = account_tree.selection()
    if not selected:
        messagebox.showerror("Error", "No account selected")
        return
    name = account_tree.item(selected[0])["values"][0]
    confirm = messagebox.askyesno("Confirm Delete", f"Delete {name}?")
    if confirm:
        vault_data.pop(name)
        vault.save_vault(vault_data, fernet)
        refresh_list()
        messagebox.showinfo("Deleted", f"{name} has been deleted")

# -------------------------------
# Buttons
# -------------------------------
tk.Button(root, text="Add Account", width=25, command=add_account).pack(pady=5)
tk.Button(root, text="View Account", width=25, command=view_account).pack(pady=5)
tk.Button(root, text="Delete Account", width=25, command=delete_account).pack(pady=5)

# -------------------------------
# Initialize
# -------------------------------
refresh_list()
root.mainloop()
