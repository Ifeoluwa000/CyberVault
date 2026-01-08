import sys
import os

# This line tells Python to look inside the 'src' folder for your files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    # Replace 'gui_dashboard' with your filename if it's different
    # This runs the code inside your dashboard file immediately
    import gui_dashboard
    print("Application started successfully.")
except ImportError as e:
    print(f"Error: Could not find the dashboard file. {e}")
except Exception as e:
    print(f"An error occurred: {e}")