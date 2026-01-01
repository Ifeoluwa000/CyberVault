import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from cryptography.fernet import Fernet
import vault
import auth
from crypto_utils import generate_key
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import string
import settings as app_settings # Make sure this import is at the top
import pyperclip


vault_data = {}  # global variable
fernet = None



def apply_global_fonts():
    global sidebar

    # Main UI font (Inter) and password font (JetBrains Mono)
    MAIN_FONT = ("Inter", "Segoe UI", "Arial")       # fallback fonts
    PASSWORD_FONT = ("JetBrains Mono", "Consolas", "Courier New")
    SIZE = 13

    style = tb.Style()
    current_theme = style.theme.name
    is_dark = "dark" in current_theme or "darkly" in current_theme
    text_color = "white" if is_dark else "#212529"

    # Theme colors
    sidebar_bg = "#343a40" if is_dark else "#f1f3f9"
    header_bg = "#3498db" if is_dark else "#9854bb"
    header_fg = "white"

    # =========================
    # GLOBAL TEXT
    # =========================
    style.configure(".", font=(MAIN_FONT, SIZE), foreground=text_color)
    style.configure("TLabel", font=(MAIN_FONT, SIZE), foreground=text_color)
    style.configure(
        "TEntry",
        font=(MAIN_FONT, SIZE),
        foreground=text_color,
        insertcolor=text_color
    )

    # =========================
    # SIDEBAR
    # =========================
    style.configure("Sidebar.TFrame", background=sidebar_bg)
    sidebar.config(style="Sidebar.TFrame")

    style.configure(
        "Sidebar.TButton",
        font=(MAIN_FONT, SIZE),
        padding=15,
        background=sidebar_bg,
        foreground=text_color,
        borderwidth=2
    )

    hover_color = "#3498db" if is_dark else "#9854bb"

    if not is_dark:
        style.configure("Sidebar.TButton", bordercolor="#9854bb")

    style.map(
        "Sidebar.TButton",
        background=[("active", hover_color)],
        foreground=[("active", "white")],
        bordercolor=[("active", hover_color)]
    )

    # =========================
    # TREEVIEW (TABLE)
    # =========================
    style.configure(
        "Treeview",
        font=(MAIN_FONT, SIZE),  # Inter for table
        rowheight=54,
        foreground=text_color,
        background="white" if not is_dark else sidebar_bg,
        fieldbackground="white" if not is_dark else sidebar_bg
    )

    style.configure(
        "Treeview.Heading",
        font=(MAIN_FONT, SIZE, "bold"),
        background=header_bg,
        foreground=header_fg,
        padding=(10, 16)
    )

    style.map(
        "Treeview.Heading",
        background=[("active", header_bg), ("pressed", header_bg)],
        foreground=[("active", header_fg)]

    )



    # =========================
    # PASSWORD FIELDS (optional)
    # =========================
    # If you have Entry widgets for passwords, set their font to PASSWORD_FONT
    # Example: password_entry.config(font=PASSWORD_FONT)


#================================
    # APP WINDOW
# ===============================


# 1. Load the saved settings immediately
saved_data = app_settings.load_settings()

# 2. Set the global policy to the SAVED data
password_policy = saved_data

# 3. Translate the saved preference into a valid theme name
saved_theme_pref = saved_data.get("theme", "darkly")

if saved_theme_pref == "light":
    actual_theme = "cosmo"
elif saved_theme_pref == "dark":
    actual_theme = "darkly"
else:
    # If it's already "cosmo" or "darkly", use it as is
    actual_theme = saved_theme_pref

# 4. Start the window with the VALID theme name
root = tb.Window(themename=actual_theme)
root.title("CyberVault - Secure Password Manager")
root.geometry("950x600")

style = tb.Style(theme=actual_theme)
# ===============================
# MASTER PASSWORD AUTH
# ===============================
root.withdraw()


def ask_master_password():
    popup = tb.Toplevel(root)
    # Check if we are in "Setup Mode" or "Login Mode"
    is_new_user = not auth.master_exists()

    popup.title("CyberVault Setup" if is_new_user else "CyberVault Login")
    popup.geometry("450x320")  # Slightly taller to fit the hint
    popup.resizable(False, False)
    popup.grab_set()

    # --- DYNAMIC TEXT SELECTION ---
    title_text = "Create Master Password" if is_new_user else "Enter Master Password"
    subtitle_text = "Choose a strong password to encrypt your vault." if is_new_user else "(Master password cannot be recovered)"
    button_text = "Create Vault" if is_new_user else "Unlock Vault"
    button_style = "success" if is_new_user else "primary"

    # Title label
    tb.Label(
        popup,
        text=title_text,
        font=("Inter", 14, "bold")
    ).pack(pady=(20, 5))

    # Subtitle/Hint label
    tb.Label(
        popup,
        text=subtitle_text,
        font=("Inter", 9, "italic")
    ).pack(pady=(0, 15))

    # Entry for master password
    master_var = tk.StringVar()
    master_entry = tb.Entry(
        popup,
        textvariable=master_var,
        show="*",
        font=("JetBrains Mono", 11)
    )
    master_entry.pack(fill="x", padx=30, pady=10)
    master_entry.focus_set()

    # Eye toggle for password visibility
    def toggle_password():
        if master_entry.cget("show") == "":
            master_entry.config(show="*")
            eye_button.config(text="👁️")
        else:
            master_entry.config(show="")
            eye_button.config(text="🔒")

    eye_button = tb.Button(
        popup,
        text="👁️",
        width=3,
        command=toggle_password,
        bootstyle="link"
    )
    eye_button.place(in_=master_entry, relx=1.0, x=-5, rely=0.5, anchor="e")

    # Submit button function
    def submit_master():
        pwd = master_var.get()
        if not pwd:
            messagebox.showerror("Error", "Password cannot be empty.", parent=popup)
            return

        if is_new_user:
            # First time setup logic
            auth.create_master(pwd)
            messagebox.showinfo("Success", "Vault initialized successfully!", parent=popup)
        else:
            # Standard login logic
            if not auth.verify_master(pwd):
                messagebox.showerror("Access Denied", "Incorrect master password.", parent=popup)
                return

        # Common logic: Generate key and enter app
        global fernet, vault_data
        key = generate_key(pwd)
        fernet = Fernet(key)

        try:
            vault_data = vault.load_vault(fernet)
        except Exception:
            vault_data = {}

        popup.destroy()
        root.deiconify()
        if 'refresh_home' in globals():  # Safety check
            refresh_home()

    # Submit Button
    tb.Button(
        popup,
        text=button_text,
        bootstyle=button_style,
        width=20,
        command=submit_master
    ).pack(pady=20)

    # Bind Enter key to submit
    popup.bind("<Return>", lambda e: submit_master())


# Call the function
ask_master_password()


# -------------------
# TOP BAR (HAMBURGER + SEARCH)
# -------------------
top_bar = tb.Frame(root)
top_bar.pack(side="top", fill="x")

search_var = tk.StringVar()

def toggle_sidebar():
    if sidebar.winfo_ismapped():
        sidebar.pack_forget()
    else:
        sidebar.pack(side="left", fill="y")


def create_hamburger(parent, command):
    hamburger_btn = tb.Frame(parent, cursor="hand2")
    hamburger_btn.pack(side="left", padx=12, pady=6)

    bars = []
    for i in range(3):
        # Create the bars
        bar = tb.Frame(hamburger_btn, width=40, height=8)
        bar.pack(pady=6)
        bars.append(bar)

    def update_colors(event=None):
        # This checks the theme right now
        style = tb.Style()
        current_theme = style.theme.name
        dark_themes = ["darkly", "cyborg", "slate", "solar", "superhero"]

        # Set to 'light' (white) if dark theme, else 'dark' (black)
        bar_color = "light" if current_theme in dark_themes else "dark"
        for bar in bars:
            bar.configure(bootstyle=bar_color)

    # Run it once to set initial color
    update_colors()

    # THE MAGIC LINE: This listens for ANY theme change in the app
    root.bind("<<ThemeChanged>>", update_colors)

    # Click events
    hamburger_btn.bind("<Button-1>", lambda e: command())
    for child in hamburger_btn.winfo_children():
        child.bind("<Button-1>", lambda e: command())

    return hamburger_btn


create_hamburger(top_bar, toggle_sidebar)
# -------------------
# Search Bar with Magnifying Glass & Placeholder
# -------------------
search_frame = tb.Frame(top_bar)
search_frame.pack(side="left", fill="x", expand=True)

# Magnifying glass icon
tb.Label(search_frame, text="🔍", font=("Segoe UI", 14)).pack(side="left", padx=6)

# Search Entry
search_entry = tb.Entry(
    search_frame,
    textvariable=search_var,
    bootstyle="info",
    font=("Segoe UI", 14)
)
search_entry.pack(side="left", fill="x", expand=True, padx=(0,6), ipady=6)

# Placeholder logic
def add_placeholder(event=None):
    if search_entry.get() == "":
        search_entry.insert(0, "Search")
        # Hex code #808080 is a medium gray visible in both light and dark backgrounds
        search_entry.config(foreground="#808080")

def remove_placeholder(event=None):
    if search_entry.get() == "Search":
        search_entry.delete(0, "end")
        # Resets to theme default (Black in Light, White in Dark)
        search_entry.config(foreground="")

# Bind events
search_entry.bind("<FocusIn>", remove_placeholder)
search_entry.bind("<FocusOut>", add_placeholder)

# Initialize
add_placeholder()
# ===============================
# MAIN AREA
# ===============================
main_area = tb.Frame(root)
main_area.pack(side="left", fill="both", expand=True, padx=15, pady=10)


# ===============================

# HOME PAGE

# ===============================

home_frame = tb.Frame(main_area)

home_frame.pack(fill="both", expand=True)


summary_frame = tb.Frame(home_frame)

summary_frame.pack(fill="x", pady=10)



total_label = tb.Label(summary_frame, bootstyle="primary")

weak_label = tb.Label(summary_frame, bootstyle="danger")

strong_label = tb.Label(summary_frame, bootstyle="success")



total_label.pack(side="left", expand=True, fill="x", padx=5)

weak_label.pack(side="left", expand=True, fill="x", padx=5)

strong_label.pack(side="left", expand=True, fill="x", padx=5)



accounts_tree = tb.Treeview(
    home_frame,
    columns=("Account", "Username"),
    show="headings",
    bootstyle=None  # Make sure no theme override
)


accounts_tree.heading("Account", text="Website", anchor="w")
accounts_tree.heading("Username", text="Username", anchor="w")

accounts_tree.column("Account", anchor="w", width=400, stretch=True)
accounts_tree.column("Username", anchor="w", width=400, stretch=True)

accounts_tree.pack(fill="both", expand=True, pady=10)

style = tb.Style()
is_dark = "dark" in style.theme.name or "darkly" in style.theme.name

if is_dark:
    accounts_tree.tag_configure("odd", background="#2b3035")
    accounts_tree.tag_configure("even", background="#212529")
else:
    accounts_tree.tag_configure("odd", background="#f9f5ff")  # soft purple
    accounts_tree.tag_configure("even", background="white")


# ===============================
# SETTINGS DICTIONARY
# ===============================
settings = {
    "theme": "dark",         # default theme
    "min_length": 8,         # password minimum length
    "require_number": True,  # password must include number
    "require_upper": True,   # password must include uppercase letter
    "require_special": True  # password must include special character
}


# ===============================
# FUNCTIONS
# ===============================
def password_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    return score, strength


def configure_zebra_tags():
    style = tb.Style()
    is_dark = "dark" in style.theme.name or "darkly" in style.theme.name

    if is_dark:
        accounts_tree.tag_configure("odd", background="#2b3035")
        accounts_tree.tag_configure("even", background="#212529")
    else:
        accounts_tree.tag_configure("odd", background="#f9f5ff")  # soft purple
        accounts_tree.tag_configure("even", background="white")


def refresh_home():
    configure_zebra_tags()

    # ---------- EMPTY STATE ----------
    if not vault_data:
        accounts_tree.pack_forget()
        empty_state_frame.pack(fill="both", expand=True)

        total_label.config(text="Total Accounts: 0")
        weak_label.config(text="Weak Passwords: 0")
        strong_label.config(text="Strong Passwords: 0")
        return

    # ---------- NORMAL STATE ----------
    empty_state_frame.pack_forget()
    accounts_tree.pack(fill="both", expand=True)

    total_accounts = len(vault_data)
    weak_count = medium_count = strong_count = 0

    for data in vault_data.values():
        score, strength = password_strength(data["password"])
        if strength == "Weak":
            weak_count += 1
        elif strength == "Medium":
            medium_count += 1
        else:
            strong_count += 1

    total_label.config(text=f"Total Accounts: {total_accounts}")
    weak_label.config(text=f"Weak Passwords: {weak_count}")
    strong_label.config(text=f"Strong Passwords: {strong_count}")

    accounts_tree.delete(*accounts_tree.get_children())

    for index, (name, data) in enumerate(vault_data.items()):
        tag = "even" if index % 2 == 0 else "odd"
        accounts_tree.insert(
            "",
            "end",
            values=(name, data["username"]),
            tags=(tag,)
        )


def build_home():
    home = tb.Frame(main_area)
    home.pack(fill="both", expand=True)

    summary_frame = tb.Frame(home)
    summary_frame.pack(fill="x", pady=10)

    global total_label, weak_label, strong_label, accounts_tree

    total_label = tb.Label(summary_frame, bootstyle="primary", style="HomeHeader.TLabel")
    weak_label = tb.Label(summary_frame, bootstyle="danger", style="HomeHeader.TLabel")
    strong_label = tb.Label(summary_frame, bootstyle="success", style="HomeHeader.TLabel")

    total_label.pack(side="left", expand=True, fill="x", padx=5)
    weak_label.pack(side="left", expand=True, fill="x", padx=5)
    strong_label.pack(side="left", expand=True, fill="x", padx=5)

    accounts_tree = tb.Treeview(
        home,
        columns=("Account", "Username"),
        show="headings",
        bootstyle="info"
    )

    accounts_tree.heading("Account", text="Account", anchor="w")
    accounts_tree.heading("Username", text="Username", anchor="w")

    accounts_tree.column("Account", anchor="w", width=250, stretch=True)
    accounts_tree.column("Username", anchor="w", width=300, stretch=True)

    accounts_tree.pack(fill="both", expand=True, pady=10)

    refresh_home()


# -------------------------------
# Show Home Page
# -------------------------------
# -------------------------------
# Show Home Page (functional)
#
def show_home():
    # Clear the analytics chart or about text from the main area
    for widget in main_area.winfo_children():
        widget.pack_forget()

    # Re-pack the home frame and call the refresh logic
    home_frame.pack(fill="both", expand=True)
    refresh_home()  # <--- This puts the data back in the table


def show_analytics():
    if not vault_data:
        messagebox.showinfo("No Data", "No accounts in vault to analyze.")
        return

    # 1. Hide the Home screen (don't destroy it!)
    for widget in main_area.winfo_children():
        widget.pack_forget()

    # 2. Create a fresh container for Analytics
    analytics_view = tb.Frame(main_area)
    analytics_view.pack(fill="both", expand=True)

    # 3. Add the Back Button (Packed at the bottom first)
    tb.Button(
        analytics_view,
        text="← Back to Home",
        bootstyle="info",
        width=26,
        command=show_home # Now calls the fixed show_home
    ).pack(side="bottom", pady=20)

    # 4. Data & Chart Logic
    df = pd.DataFrame.from_dict(vault_data, orient="index")
    df["Strength"] = df["password"].apply(lambda x: password_strength(x)[1])
    strength_counts = df["Strength"].value_counts().reindex(["Weak", "Medium", "Strong"], fill_value=0)

    chart_frame = tb.Frame(analytics_view)
    chart_frame.pack(fill="both", expand=True)

    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    sns.barplot(x=strength_counts.index, y=strength_counts.values, palette="viridis", ax=ax)
    ax.set_title("Password Strength Distribution")

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_settings():
    # Clear main_area
    for widget in main_area.winfo_children():
        widget.pack_forget()

    settings_frame = tb.Frame(main_area)
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tb.Label(settings_frame, text="Settings", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Theme Selection - Pull from current global policy
    tb.Label(settings_frame, text="Theme Selection", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5))

    # Logic to set radio button based on theme name
    current_theme_val = "light" if password_policy.get("theme") == "cosmo" else "dark"
    theme_var = tk.StringVar(value=current_theme_val)

    def change_theme():
        target_theme = "cosmo" if theme_var.get() == "light" else "darkly"
        style.theme_use(target_theme)
        apply_global_fonts()

    tb.Radiobutton(settings_frame, text="Light", variable=theme_var, value="light", bootstyle="secondary",
                   command=change_theme).pack(anchor="w")
    tb.Radiobutton(settings_frame, text="Dark", variable=theme_var, value="dark", bootstyle="secondary",
                   command=change_theme).pack(anchor="w")

    # Password Policy Preferences - Pull from current global policy
    tb.Label(settings_frame, text="Password Policy Preferences", font=("Segoe UI", 12, "bold")).pack(anchor="w",
                                                                                                     pady=(20, 5))

    min_length_var = tk.IntVar(value=password_policy.get("min_length", 8))
    require_number_var = tk.BooleanVar(value=password_policy.get("require_number", True))
    require_upper_var = tk.BooleanVar(value=password_policy.get("require_upper", True))
    require_special_var = tk.BooleanVar(value=password_policy.get("require_special", True))

    tb.Label(settings_frame, text="Minimum Password Length:").pack(anchor="w")
    tb.Entry(settings_frame, textvariable=min_length_var, width=5).pack(anchor="w", pady=2)
    tb.Checkbutton(settings_frame, text="Require Number", variable=require_number_var, bootstyle="secondary").pack(
        anchor="w")
    tb.Checkbutton(settings_frame, text="Require Uppercase Letter", variable=require_upper_var,
                   bootstyle="secondary").pack(anchor="w")
    tb.Checkbutton(settings_frame, text="Require Special Character", variable=require_special_var,
                   bootstyle="secondary").pack(anchor="w")

    def save_settings_action():
        global password_policy

        # Update the dictionary
        password_policy = {
            "theme": "cosmo" if theme_var.get() == "light" else "darkly",
            "min_length": min_length_var.get(),
            "require_number": require_number_var.get(),
            "require_upper": require_upper_var.get(),
            "require_special": require_special_var.get()
        }

        # 🔥 SAVE TO FILE
        app_settings.save_settings(password_policy)

        messagebox.showinfo("Saved", "Settings saved successfully.")
        show_home()

    btn_frame = tb.Frame(settings_frame)
    btn_frame.pack(pady=20)
    tb.Button(btn_frame, text="Save Settings", bootstyle="success", command=save_settings_action).pack(side="left",
                                                                                                       padx=5)
    tb.Button(btn_frame, text="Cancel", bootstyle="secondary", command=show_home).pack(side="left", padx=10)

def add_account():
    popup = tb.Toplevel(root)
    popup.title("Add New Account")
    popup.geometry("700x750")
    popup.resizable(False, False)
    popup.grab_set()

    # --- UPDATED SUGGESTION LOGIC (CHECKBOX STYLE) ---
    suggest_var = tb.BooleanVar(value=False) # Tracks if checkbox is ticked

    def handle_suggestion():
        if suggest_var.get():
            # Generate and insert
            length = 16
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            strong_pwd = ''.join(random.choice(chars) for _ in range(length))
            pass_entry.delete(0, 'end')
            pass_entry.insert(0, strong_pwd)
            update_strength()
        else:
            # Clear if unchecked so they can type their own
            pass_entry.delete(0, 'end')
            update_strength()

    # ----------------------------------------------

    tb.Label(popup, text="Add Account", font=("Inter", 15, "bold")).pack(pady=10)

    # Website Name
    tb.Label(popup, text="Website Name").pack(anchor="w", padx=20)
    name_entry = tb.Entry(popup)
    name_entry.pack(fill="x", padx=20, pady=5)

    # Username / Email
    tb.Label(popup, text="Username / Email").pack(anchor="w", padx=20)
    user_entry = tb.Entry(popup)
    user_entry.pack(fill="x", padx=20, pady=5)

    # Password
    tb.Label(popup, text="Password").pack(anchor="w", padx=20)
    pass_entry = tb.Entry(popup, show="*", font=("JetBrains Mono", 11))
    pass_entry.pack(fill="x", padx=20, pady=5)

    # Strength feedback
    strength_label = tb.Label(popup, text="Strength: ", font=("Inter", 10))
    strength_label.pack(anchor="w", padx=20, pady=(2, 5))

    # --- THE CHECKBOX ---
    tb.Checkbutton(
        popup,
        text="Suggest a strong password",
        variable=suggest_var,
        command=handle_suggestion,
        bootstyle="info-square-toggle" # Makes it look like a modern toggle
    ).pack(anchor="w", padx=20, pady=5)

    # Eye icon toggle
    def toggle_password():
        if pass_entry.cget("show") == "":
            pass_entry.config(show="*")
            eye_button.config(text="👁️")
        else:
            pass_entry.config(show="")
            eye_button.config(text="🔒")

    eye_button = tb.Button(popup, text="👁️", width=3, command=toggle_password)
    eye_button.place(in_=pass_entry, relx=1.0, x=-5, rely=0.5, anchor="e")

    # Notes
    tb.Label(popup, text="Notes").pack(anchor="w", padx=20, pady=(10,0))
    notes_entry = tb.Text(popup, height=4)
    notes_entry.pack(fill="x", padx=20, pady=5)

    # Real-time validation
    def update_strength(event=None):
        pwd = pass_entry.get()
        if not pwd:
            strength_label.config(text="Strength: ", bootstyle="default")
            return

        score, strength = password_strength(pwd)
        errors = []
        if len(pwd) < password_policy["min_length"]:
            errors.append(f"Min length: {password_policy['min_length']}")
        if password_policy["require_number"] and not re.search(r"[0-9]", pwd):
            errors.append("Must include a number")
        if password_policy["require_upper"] and not re.search(r"[A-Z]", pwd):
            errors.append("Must include uppercase")
        if password_policy["require_special"] and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
            errors.append("Must include special char")

        if errors:
            strength_label.config(text="Password invalid: " + ", ".join(errors), bootstyle="danger")
        else:
            color = {"Weak": "danger", "Medium": "warning", "Strong": "success"}[strength]
            strength_label.config(text=f"Strength: {strength}", bootstyle=color)

    pass_entry.bind("<KeyRelease>", update_strength)

    # Save account
    def save_account():
        name = name_entry.get().strip()
        username = user_entry.get().strip()
        password = pass_entry.get().strip()
        notes = notes_entry.get("1.0", "end").strip()

        if not name or not username or not password:
            messagebox.showerror("Error", "Please fill all required fields.", parent=popup)
            return

        if "Password invalid" in strength_label.cget("text"):
            messagebox.showerror("Error", "Password does not meet policy requirements.", parent=popup)
            return

        vault_data[name] = {"username": username, "password": password, "notes": notes}
        vault.save_vault(vault_data, fernet)
        popup.destroy()
        messagebox.showinfo("Success", "Account saved successfully.")
        refresh_home()

    # Buttons
    btn_frame = tb.Frame(popup)
    btn_frame.pack(pady=20)
    tb.Button(btn_frame, text="SAVE ACCOUNT", bootstyle="success", width=18, command=save_account).pack(side="left", padx=8)
    tb.Button(btn_frame, text="Cancel", bootstyle="secondary", width=12, command=popup.destroy).pack(side="left", padx=8)

# -------- EMPTY STATE (HOME) --------
empty_state_frame = tb.Frame(home_frame)

tb.Label(
    empty_state_frame,
    text="🔐",
    font=("Segoe UI", 48)
).pack(pady=(50, 10))

tb.Label(
    empty_state_frame,
    text="Welcome to CyberVault",
    font=("Segoe UI", 25, "bold")
).pack(pady=5)

tb.Label(
    empty_state_frame,
    text="Your security starts here. Add your first account to begin.",
    font=("Segoe UI", 18)
).pack(pady=(0, 20))

tb.Button(
    empty_state_frame,
    text="➕ CREATE YOUR FIRST ACCOUNT",
    bootstyle="success",
    width=35,
    command=add_account
).pack()


def view_account():
    # 1. Get selection from the Treeview
    selected = accounts_tree.focus()
    if not selected:
        messagebox.showwarning("Select", "Please select an account from the list first.")
        return

    # 2. Extract data
    try:
        name = accounts_tree.item(selected)["values"][0]
        data = vault_data[name]
    except Exception as e:
        messagebox.showerror("Error", f"Could not load account data: {e}")
        return

    # --- STYLE SETTINGS ---
    THEME_COLOR = "info"
    TITLE_FONT = ("Segoe UI", 22, "bold")
    LABEL_FONT = ("Segoe UI", 10, "bold")
    DATA_FONT = ("Segoe UI", 12)

    def show_view_screen():
        """Displays the account details in high-contrast Read-Only mode."""
        for widget in main_area.winfo_children():
            widget.pack_forget()

        view_frame = tb.Frame(main_area)
        view_frame.pack(fill="both", expand=True, padx=60, pady=40)

        # Header
        tb.Label(
            view_frame,
            text="ACCOUNT DETAILS",
            font=TITLE_FONT,
            bootstyle=THEME_COLOR
        ).pack(anchor="w", pady=(0, 30))

        # Detail Rows
        def create_detail_block(label, text, is_password=False):
            container = tb.Frame(view_frame)
            container.pack(fill="x", pady=15)

            tb.Label(
                container,
                text=label,
                font=LABEL_FONT,
                bootstyle=THEME_COLOR
            ).pack(anchor="w")

            data_row = tb.Frame(container)
            data_row.pack(fill="x", pady=(2, 0))

            tb.Label(
                data_row,
                text=text,
                font=DATA_FONT
            ).pack(side="left")

            if is_password:
                def copy_func():
                    pyperclip.copy(text)
                    messagebox.showinfo("Copied", "Password copied to clipboard!")

                tb.Button(
                    data_row,
                    text="📋 Copy Password",
                    bootstyle=f"{THEME_COLOR}-link",
                    command=copy_func
                ).pack(side="left", padx=10)

        create_detail_block("WEBSITE NAME", name)
        create_detail_block("USERNAME", data["username"])
        create_detail_block("PASSWORD", data["password"], is_password=True)

        # Notes
        tb.Label(
            view_frame,
            text="NOTES",
            font=LABEL_FONT,
            bootstyle=THEME_COLOR
        ).pack(anchor="w", pady=(20, 5))

        tb.Label(
            view_frame,
            text=data["notes"] if data["notes"] else "---",
            font=DATA_FONT,
            wraplength=550,
            justify="left"
        ).pack(anchor="w", padx=2)

        # Navigation Buttons
        btn_frame = tb.Frame(view_frame)
        btn_frame.pack(side="bottom", fill="x", pady=20)

        tb.Button(
            btn_frame,
            text="EDIT ACCOUNT",
            bootstyle=THEME_COLOR,
            width=18,
            command=show_edit_screen
        ).pack(side="left", padx=5)

        tb.Button(
            btn_frame,
            text="BACK",
            bootstyle="secondary-outline",
            width=12,
            command=show_home
        ).pack(side="left", padx=5)

    def show_edit_screen():
        """Displays the modification form with real-time strength validation and suggestion."""
        for widget in main_area.winfo_children():
            widget.pack_forget()

        edit_frame = tb.Frame(main_area)
        edit_frame.pack(fill="both", expand=True, padx=60, pady=40)

        tb.Label(
            edit_frame,
            text="MODIFY ACCOUNT",
            font=TITLE_FONT,
            bootstyle=THEME_COLOR
        ).pack(anchor="w", pady=(0, 30))

        # Inputs
        tb.Label(
            edit_frame,
            text="WEBSITE NAME",
            font=LABEL_FONT,
            bootstyle=THEME_COLOR
        ).pack(anchor="w")

        name_entry = tb.Entry(edit_frame, font=DATA_FONT)
        name_entry.insert(0, name)
        name_entry.pack(fill="x", pady=(5, 15))

        tb.Label(
            edit_frame,
            text="USERNAME / EMAIL",
            font=LABEL_FONT,
            bootstyle=THEME_COLOR
        ).pack(anchor="w")

        user_entry = tb.Entry(edit_frame, font=DATA_FONT)
        user_entry.insert(0, data["username"])
        user_entry.pack(fill="x", pady=(5, 15))

        # Password + Eye + Strength
        tb.Label(
            edit_frame,
            text="PASSWORD",
            font=LABEL_FONT,
            bootstyle=THEME_COLOR
        ).pack(anchor="w")

        pass_container = tb.Frame(edit_frame)
        pass_container.pack(fill="x", pady=(5, 0))

        pass_entry = tb.Entry(
            pass_container,
            font=("JetBrains Mono", 12),
            show="*"
        )
        pass_entry.insert(0, data["password"])
        pass_entry.pack(side="left", fill="x", expand=True)

        # --- SUGGESTION LOGIC ---
        suggest_var = tb.BooleanVar(value=False)

        def handle_suggestion():
            if suggest_var.get():
                # Import here to ensure availability
                import random
                import string
                length = 16
                chars = string.ascii_letters + string.digits + "!@#$%^&*"
                strong_pwd = ''.join(random.choice(chars) for _ in range(length))
                pass_entry.config(show="") # Show the generated password so user can see it
                pass_entry.delete(0, 'end')
                pass_entry.insert(0, strong_pwd)
                eye_btn.config(text="🔒")
                update_strength()
        # ------------------------

        def toggle_password():
            new_show = "" if pass_entry.cget("show") == "*" else "*"
            pass_entry.config(show=new_show)
            eye_btn.config(text="🔒" if new_show == "" else "👁️")

        eye_btn = tb.Button(
            pass_container,
            text="👁️",
            bootstyle="secondary-link",
            command=toggle_password
        )
        eye_btn.pack(side="left", padx=5)

        strength_label = tb.Label(
            edit_frame,
            text="Strength: ",
            font=("Segoe UI", 9)
        )
        strength_label.pack(anchor="w", pady=(2, 0))

        # --- THE CHECKBOX ---
        tb.Checkbutton(
            edit_frame,
            text="Suggest a strong password",
            variable=suggest_var,
            command=handle_suggestion,
            bootstyle="info-square-toggle"
        ).pack(anchor="w", pady=(5, 15))

        def update_strength(event=None):
            pwd = pass_entry.get()
            if not pwd:
                strength_label.config(text="Strength: ", bootstyle="default")
                return

            errors = []
            if len(pwd) < password_policy["min_length"]:
                errors.append(f"Min length: {password_policy['min_length']}")
            if password_policy["require_number"] and not re.search(r"[0-9]", pwd):
                errors.append("Need number")
            if password_policy["require_upper"] and not re.search(r"[A-Z]", pwd):
                errors.append("Need uppercase")
            if password_policy["require_special"] and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
                errors.append("Need special character")

            if errors:
                strength_label.config(
                    text="⚠️ Policy: " + ", ".join(errors),
                    bootstyle="danger"
                )
            else:
                score, strength = password_strength(pwd)
                color = {"Weak": "danger", "Medium": "warning", "Strong": "success"}[strength]
                strength_label.config(
                    text=f"✅ Strength: {strength}",
                    bootstyle=color
                )

        pass_entry.bind("<KeyRelease>", update_strength)
        update_strength()

        # Notes
        tb.Label(
            edit_frame,
            text="NOTES",
            font=LABEL_FONT,
            bootstyle=THEME_COLOR
        ).pack(anchor="w")

        notes_text = tk.Text(
            edit_frame,
            height=4,
            font=DATA_FONT,
            relief="flat",
            highlightthickness=1
        )
        notes_text.insert("1.0", data["notes"])
        notes_text.pack(fill="x", pady=(5, 15))

        def validate_and_save():
            new_name = name_entry.get().strip()
            new_pass = pass_entry.get()
            new_user = user_entry.get().strip()

            if not new_name or not new_pass or not new_user:
                messagebox.showerror("Error", "Missing required fields.")
                return

            if "Policy:" in strength_label.cget("text"):
                messagebox.showerror(
                    "Policy Violation",
                    "Fix password requirements first."
                )
                return

            # Update the global vault_data
            if new_name != name:
                del vault_data[name]

            vault_data[new_name] = {
                "username": new_user,
                "password": new_pass,
                "notes": notes_text.get("1.0", "end-1c")
            }

            # Call the global save function
            vault.save_vault(vault_data, fernet)
            messagebox.showinfo("Success", "Account Modified!")
            show_home()

        btn_frame = tb.Frame(edit_frame)
        btn_frame.pack(side="bottom", fill="x", pady=20)

        tb.Button(
            btn_frame,
            text="UPDATE NOW",
            bootstyle="success",
            width=18,
            command=validate_and_save
        ).pack(side="left", padx=5)

        tb.Button(
            btn_frame,
            text="CANCEL",
            bootstyle="secondary-outline",
            width=12,
            command=show_view_screen
        ).pack(side="left", padx=5)

    # 🔥 Start the flow
    show_view_screen()




def delete_account():
    selected = accounts_tree.focus()
    if not selected:
        messagebox.showwarning("Selection Required", "Please select an account from the list to delete.")
        return

    # Get the account name from the Treeview
    name = accounts_tree.item(selected)["values"][0]

    # Professional confirmation with a 'Warning' icon
    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Are you sure you want to permanently delete the account: '{name}'?\n\n"
        "This action cannot be undone.",
        icon='warning'
    )

    if confirm:
        try:
            # Remove from dictionary
            vault_data.pop(name)

            # Save the updated vault to the encrypted file
            vault.save_vault(vault_data, fernet)

            # Refresh the UI to show the account is gone


            messagebox.showinfo("Deleted", f"Successfully removed '{name}' from your vault.")
            refresh_home()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete account: {e}")
def search_accounts(*args):
    query = search_var.get().lower()
    accounts_tree.delete(*accounts_tree.get_children())

    # Filter matching accounts
    filtered_accounts = {
        name: data
        for name, data in vault_data.items()
        if query in name.lower() or query in data["username"].lower()
    }

    # Insert with zebra tags
    for index, (name, data) in enumerate(filtered_accounts.items()):
        tag = "even" if index % 2 == 0 else "odd"
        accounts_tree.insert("", "end", values=(name, data["username"]), tags=(tag,))


def show_about():
    # Clear the main area first
    for widget in main_area.winfo_children():
        widget.pack_forget()

    # Create the About Page layout
    about_frame = tb.Frame(main_area)
    about_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Header
    tb.Label(about_frame, text="ℹ️ About CyberVault", font=("Segoe UI", 24, "bold")).pack(pady=10)
    tb.Label(about_frame, text="Version 1.0.0", font=("Segoe UI", 12), bootstyle="secondary").pack()

    # Short Description
    description = (
        "🔐 CyberVault is a secure password manager that keeps your accounts safe.\n"
        "All data is encrypted with Fernet for privacy.\n"
        "Designed by Ojo Ifeoluwa Wonders.\n"
        "🌐 GitHub: https://github.com/Ifeoluwa000/CyberVault"
    )
    tb.Label(about_frame, text=description, wraplength=600, justify="left").pack(pady=30)

    # Back button
    tb.Button(about_frame, text="Back to Home", bootstyle="outline-info", command=show_home).pack(pady=10)




# Now configure your custom sidebar button style
style.configure('Sidebar.TButton', font=('Segoe UI', 12))

style.configure("Home.TLabel", font=("Segoe UI", 14))
style.configure("HomeHeader.TLabel", font=("Segoe UI", 15, "bold"))

style.configure(
    "Treeview",
    font=("Quicksand", 12),
    rowheight=40
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 15, "bold")
)



# ===============================
# SIDEBAR (HIDDEN)
# ===============================
sidebar = tb.Frame(root, width=320)
sidebar.pack_propagate(False)
sidebar.pack_forget()  # initially hidden


# Create a custom style for bigger buttons
style.configure('Sidebar.TButton', font=('Segoe UI', 12))

#Home button
tb.Button(
    sidebar,
    text="🏠  Home",
    width=26,
    bootstyle="info",
    style='Sidebar.TButton',
    command=show_home
).pack(pady=8)


# Sidebar - Accounts Dropdown
accounts_frame = tb.Frame(sidebar)
accounts_frame.pack(fill="x", pady=(5, 0))

def toggle_accounts_dropdown():
    if accounts_buttons_frame.winfo_ismapped():
        accounts_buttons_frame.pack_forget()
    else:
        accounts_buttons_frame.pack(fill="x", padx=10, pady=5)
#Accounts button
tb.Button(
    accounts_frame,
    text="📁  Accounts  ▼",
    width=26,
    bootstyle="info",
    style='Sidebar.TButton',
    command=toggle_accounts_dropdown
).pack(fill="x")

# Frame containing the three buttons (initially hidden)
accounts_buttons_frame = tb.Frame(accounts_frame)

# We use the bootstyle name + the style name (e.g., success.Sidebar.TButton)
tb.Button(accounts_buttons_frame,
          text="➕ Add Account",
          bootstyle="success",
          style='success.Sidebar.TButton',
          command=add_account).pack(fill="x", pady=5)

tb.Button(accounts_buttons_frame,
          text="👁 View Account",
          bootstyle="primary",
          style='primary.Sidebar.TButton',
          command=view_account).pack(fill="x", pady=5)

tb.Button(accounts_buttons_frame,
          text="🗑 Delete Account",
          bootstyle="danger",
          style='danger.Sidebar.TButton',
          command=delete_account).pack(fill="x", pady=5)
# Other sidebar buttons
tb.Button(
    sidebar,
    text="📊  Analytics",
    width=26,
    bootstyle="info",
    style='Sidebar.TButton',
    command=show_analytics
).pack(pady=8)

# Settings Button (Matches Home characteristics)
tb.Button(sidebar,
          text="⚙️ Settings",
          width=26,
          bootstyle="info",
          style='Sidebar.TButton',
          command=show_settings).pack(pady=8)

# About Button (Matches Home characteristics but stays at the bottom)
tb.Button(sidebar,
          text="ℹ️ About",
          width=26,
          bootstyle="info",
          style='Sidebar.TButton',
          command=show_about).pack(side="bottom", pady=8)
# ===============================
# BINDINGS & START
# ===============================
search_var.trace_add("write", search_accounts)
refresh_home()
apply_global_fonts()
root.mainloop()
