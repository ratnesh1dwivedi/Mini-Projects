import tkinter as tk
from tkinter import messagebox
import re

# List of common passwords or dictionary words for the uniqueness check
COMMON_PASSWORDS = ["password", "123456", "12345678", "qwerty", "abc123"]

def check_password_strength(password):
    strength = {
        "length_score": 0,
        "complexity_score": 0,
        "uniqueness_score": 0,
        "suggestions": []
    }
    
    # Check Length
    if len(password) < 8:
        strength["suggestions"].append("Password should be at least 8 characters long.")
    elif 8 <= len(password) <= 10:
        strength["length_score"] = 1
    elif 11 <= len(password) <= 14:
        strength["length_score"] = 2
    else:
        strength["length_score"] = 3

    # Check Complexity
    if re.search(r'[A-Z]', password):
        strength["complexity_score"] += 1
    else:
        strength["suggestions"].append("Add at least one uppercase letter.")
        
    if re.search(r'[a-z]', password):
        strength["complexity_score"] += 1
    else:
        strength["suggestions"].append("Add at least one lowercase letter.")
        
    if re.search(r'[0-9]', password):
        strength["complexity_score"] += 1
    else:
        strength["suggestions"].append("Add at least one digit.")
        
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength["complexity_score"] += 1
    else:
        strength["suggestions"].append("Add at least one special character (e.g., !, @, #).")

    # Check Uniqueness
    if any(common_pass in password.lower() for common_pass in COMMON_PASSWORDS):
        strength["suggestions"].append("Avoid using common words or sequences.")
    else:
        strength["uniqueness_score"] = 1

    # Calculate Total Score
    total_score = strength["length_score"] + strength["complexity_score"] + strength["uniqueness_score"]

    # Determine Strength Level
    if total_score >= 6:
        strength["level"] = "Very Strong"
    elif total_score >= 4:
        strength["level"] = "Strong"
    elif total_score >= 2:
        strength["level"] = "Fair"
    else:
        strength["level"] = "Weak"
    
    return strength

def on_password_change(event):
    password = password_entry.get()
    
    if not password:
        strength_label.config(text="Enter a password to check its strength", fg="black")
        suggestions_text.config(state=tk.NORMAL)
        suggestions_text.delete(1.0, tk.END)
        suggestions_text.config(state=tk.DISABLED)
        return
    
    try:
        strength = check_password_strength(password)
        strength_level = strength["level"]
        
        if strength_level == "Very Strong":
            strength_label.config(text="Very Strong", fg="green")
        elif strength_level == "Strong":
            strength_label.config(text="Strong", fg="blue")
        elif strength_level == "Fair":
            strength_label.config(text="Fair", fg="orange")
        else:
            strength_label.config(text="Weak", fg="red")
        
        # Display suggestions
        suggestions_text.config(state=tk.NORMAL)
        suggestions_text.delete(1.0, tk.END)
        if strength['suggestions']:
            suggestions_text.insert(tk.END, "Suggestions:\n")
            for suggestion in strength['suggestions']:
                suggestions_text.insert(tk.END, f"- {suggestion}\n")
        else:
            suggestions_text.insert(tk.END, "No suggestions. Your password is strong!")
        suggestions_text.config(state=tk.DISABLED)
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def on_submit():
    password = password_entry.get()
    if not password:
        messagebox.showwarning("Input Error", "Please enter a password.")
    else:
        strength = check_password_strength(password)
        messagebox.showinfo("Password Strength", f"Your password is {strength['level']}")

# Create the main application window
root = tk.Tk()
root.title("Password Strength Checker")
root.geometry("400x300")

# Password Entry
tk.Label(root, text="Enter Password:").pack(pady=10)
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack()
password_entry.bind("<KeyRelease>", on_password_change)

# Strength Label
strength_label = tk.Label(root, text="Enter a password to check its strength", font=('Helvetica', 12))
strength_label.pack(pady=10)

# Suggestions Text Box
suggestions_text = tk.Text(root, height=8, width=50, state=tk.DISABLED)
suggestions_text.pack(pady=10)

# Submit Button
submit_button = tk.Button(root, text="Check Password Strength", command=on_submit)
submit_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
