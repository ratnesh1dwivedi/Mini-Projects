import hashlib
import random
import string
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Import ttk for Progressbar

# Function to hash the password
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Function to generate password candidates with randomized order
def generate_candidates(num_small, num_capital, num_digits, num_symbols):
    # Define character sets
    small_letters = string.ascii_lowercase
    capital_letters = string.ascii_uppercase
    digits = string.digits
    symbols = r"!@#$%^&*()_+-=[]{};':,./<>?"

    # Generate random password candidates
    candidates = []
    for _ in range(10_000):  # Generate 10,000 random candidates
        password = []

        # Generate small letters
        password.extend(random.sample(small_letters, num_small))

        # Generate capital letters
        password.extend(random.sample(capital_letters, num_capital))

        # Generate digits
        password.extend(random.sample(digits, num_digits))

        # Generate symbols
        password.extend(random.sample(symbols, num_symbols))

        # Shuffle the password characters
        random.shuffle(password)

        # Join the characters to form the password string
        candidates.append(''.join(password))

    return candidates

# Function to save generated candidates to a file
def save_candidates_to_file(candidates, filename):
    try:
        with open(filename, 'w') as file:
            for candidate in candidates:
                file.write(candidate + '\n')
        messagebox.showinfo("Success", f"Dictionary saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save dictionary: {e}")

# Function to crack the hashed password using dictionary attack
def dictionary_attack(hashed_password, num_small, num_capital, num_digits, num_symbols, progress_var):
    try:
        candidates = generate_candidates(num_small, num_capital, num_digits, num_symbols)
        total_candidates = len(candidates)
        for i, password in enumerate(candidates):
            if hash_password(password) == hashed_password:
                progress_var.set(100)  # Set progress to 100% when password found
                return password
            progress_var.set((i + 1) * 100 // total_candidates)  # Update progress percentage
    except Exception as e:
        messagebox.showerror("Error", f"Dictionary attack error: {e}")

    progress_var.set(100)  # Set progress to 100% if no password found
    return None

# Function to handle start button click
def on_start():
    num_small = int(small_letters_var.get() or 0)
    num_capital = int(capital_letters_var.get() or 0)
    num_digits = int(digits_var.get() or 0)
    num_symbols = int(symbols_var.get() or 0)
    hashed_password = hashed_password_var.get() or None
    attack_mode = attack_mode_var.get()

    try:
        if not (num_small > 0 or num_capital > 0 or num_digits > 0 or num_symbols > 0):
            messagebox.showwarning("Warning", "Please specify at least one type of character.")
            return

        if attack_mode == 'dictionary':
            progress_var.set(0)  # Initialize progress bar
            progress_window = tk.Toplevel()
            progress_window.title("Password Cracking Progress")
            progress_bar = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, mode='determinate')
            progress_bar.pack(padx=10, pady=10)
            progress_var.set(1)  # Start progress
            threading.Thread(target=lambda: dictionary_attack(hashed_password, num_small, num_capital, num_digits, num_symbols, progress_var)).start()
            
            # Save dictionary automatically
            candidates = generate_candidates(num_small, num_capital, num_digits, num_symbols)
            filename = f"password_dictionary_{num_small}_{num_capital}_{num_digits}_{num_symbols}.txt"
            save_candidates_to_file(candidates, filename)

        elif attack_mode == 'live':
            progress_var.set(0)  # Initialize progress bar
            progress_window = tk.Toplevel()
            progress_window.title("Password Cracking Progress")
            progress_bar = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, mode='determinate')
            progress_bar.pack(padx=10, pady=10)
            progress_var.set(1)  # Start progress
            threading.Thread(target=lambda: live_attack(hashed_password, num_small, num_capital, num_digits, num_symbols, progress_var)).start()

    except ValueError as ve:
        messagebox.showerror("Error", f"Invalid input: {ve}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to save generated dictionary to a file (no longer used directly)
def save_dictionary():
    pass  # This function is no longer needed for direct user interaction

# GUI Setup
root = tk.Tk()
root.title("Advanced Password Cracker")

# Initialize variables for GUI components
small_letters_var = tk.StringVar()
capital_letters_var = tk.StringVar()
digits_var = tk.StringVar()
symbols_var = tk.StringVar()
hashed_password_var = tk.StringVar()
attack_mode_var = tk.StringVar(value='live')  # Default to live attack mode
progress_var = tk.IntVar()

# Create main frame
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Labels and Entry fields for character specifications
tk.Label(frame, text="Number of Small Letters:").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=small_letters_var).grid(row=0, column=1, sticky="w")

tk.Label(frame, text="Number of Capital Letters:").grid(row=1, column=0, sticky="w")
tk.Entry(frame, textvariable=capital_letters_var).grid(row=1, column=1, sticky="w")

tk.Label(frame, text="Number of Digits:").grid(row=2, column=0, sticky="w")
tk.Entry(frame, textvariable=digits_var).grid(row=2, column=1, sticky="w")

tk.Label(frame, text="Number of Symbols:").grid(row=3, column=0, sticky="w")
tk.Entry(frame, textvariable=symbols_var).grid(row=3, column=1, sticky="w")

tk.Label(frame, text="Optional Hashed Password:").grid(row=4, column=0, sticky="w")
tk.Entry(frame, textvariable=hashed_password_var).grid(row=4, column=1, sticky="w")

# Radio buttons for Attack Mode selection
tk.Label(frame, text="Select Attack Mode:").grid(row=5, column=0, sticky="w")
tk.Radiobutton(frame, text="Live Attack", variable=attack_mode_var, value='live').grid(row=5, column=1, sticky="w")
tk.Radiobutton(frame, text="Dictionary Attack", variable=attack_mode_var, value='dictionary').grid(row=5, column=2, sticky="w")

# Button to start the password cracking process
tk.Button(frame, text="Start", command=on_start).grid(row=6, column=0, columnspan=3, pady=10)

# Run the main GUI event loop
root.mainloop()
