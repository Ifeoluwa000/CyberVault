import tkinter as tk
from tkinter import simpledialog, messagebox
from cryptography.fernet import Fernet
from crypto_utils import generate_key
import vault
import auth
import re

# -------------------------------
# Password Strength Checker
# -------------------------------
def password_strength(password):
    """
    Returns a score and message for password strength
    """
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
# Step 1: Ask for master password
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
# Step 2: Setup encryption key
# -------------------------------
key = generate_key(master_password)
fernet = Fernet(key)

# -------------------------------
# Step 3: Load vault data
# -------------------------------
vault_data = vault.load_vault(fernet)

# -------------------------------
# Step 4: Create main window
# -------------------------------
root = tk.Tk()
root.title("CipherVault Dashboard")
root.geometry("450x450")

# Listbox to show stored accounts
account_listbox = tk.Listbox(root, width=50)
account_listbox.pack(pady=20)

# -------------------------------
# Step 5: Functions
# -------------------------------
def refresh_list():
    account_listbox.delete(0, tk.END)
    for account in vault_data:
        account_listbox.insert(tk.END, account)

def add_account():
    name = simpledialog.askstring("Account Name", "Enter Account Name:")
    username = simpledialog.askstring("Username/Email", "Enter Username/Email:")
    password = simpledialog.askstring("Password", "Enter Password:")

    if not (name and username and password):
        messagebox.showerror("Error", "All fields are required")
        return

    # Check password strength
    score, strength = password_strength(password)
    if strength == "Weak":
        proceed = messagebox.askyesno(
            "Weak Password",
            f"This password is weak. Do you still want to use it?"
        )
        if not proceed:
            return

    vault_data[name] = {"username": username, "password": password}
    vault.save_vault(vault_data, fernet)
    refresh_list()
    messagebox.showinfo("Success", f"{name} added! Password strength: {strength}")

def view_account():
    selected = account_listbox.curselection()
    if not selected:
        messagebox.showerror("Error", "No account selected")
        return

    name = account_listbox.get(selected[0])
    data = vault_data[name]
    messagebox.showinfo(
        name,
        f"Username: {data['username']}\nPassword: {data['password']}"
    )

def delete_account():
    selected = account_listbox.curselection()
    if not selected:
        messagebox.showerror("Error", "No account selected")
        return

    name = account_listbox.get(selected[0])
    confirm = messagebox.askyesno("Confirm Delete", f"Delete {name}?")
    if confirm:
        vault_data.pop(name)
        vault.save_vault(vault_data, fernet)
        refresh_list()
        messagebox.showinfo("Deleted", f"{name} has been deleted")

# -------------------------------
# Step 6: Buttons
# -------------------------------
tk.Button(root, text="Add Account", width=20, command=add_account).pack(pady=5)
tk.Button(root, text="View Account", width=20, command=view_account).pack(pady=5)
tk.Button(root, text="Delete Account", width=20, command=delete_account).pack(pady=5)

# Initial population
refresh_list()
root.mainloop()
