import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class Rotor:
    def __init__(self, wiring, notch):
        self.wiring = wiring
        self.notch = ord(notch) - ord('A')
        self.position = 0

    def rotate(self):
        self.position = (self.position + 1) % 26
        return self.position == self.notch

    def set_position(self, char):
        self.position = ord(char.upper()) - ord('A')

    def forward(self, c):
        index = (ord(c) - ord('A') + self.position) % 26
        return chr((ord(self.wiring[index]) - ord('A') - self.position + 26) % 26 + ord('A'))

    def backward(self, c):
        index = (self.wiring.index(chr((ord(c) - ord('A') + self.position) % 26 + ord('A'))) - self.position + 26) % 26
        return chr(index + ord('A'))

class Reflector:
    def __init__(self, wiring):
        self.wiring = wiring

    def reflect(self, c):
        return self.wiring[ord(c) - ord('A')]

class Plugboard:
    def __init__(self, wiring='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        self.wiring = wiring

    def swap(self, c):
        return self.wiring[ord(c) - ord('A')]

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard

    def encode(self, letter):
        letter = self.plugboard.swap(letter)
        for rotor in self.rotors:
            letter = rotor.forward(letter)
        letter = self.reflector.reflect(letter)
        for rotor in reversed(self.rotors):
            letter = rotor.backward(letter)
        letter = self.plugboard.swap(letter)
        return letter

    def rotate_rotors(self):
        rotate_next = self.rotors[0].rotate()
        for i in range(1, len(self.rotors)):
            if rotate_next:
                rotate_next = self.rotors[i].rotate()
            else:
                break

    def process_message(self, message):
        encoded_message = ''
        for letter in message:
            if letter.isalpha():
                self.rotate_rotors()
                encoded_message += self.encode(letter.upper())
            else:
                encoded_message += letter
        return encoded_message

def on_encode_decode(action):
    try:
        message = input_text.get("1.0", tk.END).strip()
        if not message:
            raise ValueError("Input message cannot be empty")

        rotor1_pos = rotor1_entry.get().upper()
        rotor2_pos = rotor2_entry.get().upper()
        rotor3_pos = rotor3_entry.get().upper()

        if not (rotor1_pos.isalpha() and rotor2_pos.isalpha() and rotor3_pos.isalpha()):
            raise ValueError("Rotor positions must be alphabetic characters (A-Z)")

        rotor1.set_position(rotor1_pos)
        rotor2.set_position(rotor2_pos)
        rotor3.set_position(rotor3_pos)

        if action == "encode":
            result_message = enigma.process_message(message)
        elif action == "decode":
            result_message = enigma.process_message(message)

        output_text.config(state=tk.NORMAL)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result_message)
        output_text.config(state=tk.DISABLED)
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# Define rotor wirings and notch positions
rotor1 = Rotor('EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'Q')  # Notch at 'Q'
rotor2 = Rotor('AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E')  # Notch at 'E'
rotor3 = Rotor('BDFHJLCPRTXVZNYEIWGAKMUSQO', 'V')  # Notch at 'V'

# Define reflector wiring
reflector = Reflector('YRUHQSLDPXNGOKMIEBFZCWVJAT')

# Define plugboard wiring (identity in this example, no swaps)
plugboard = Plugboard('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

# Create Enigma machine with 3 rotors, a reflector, and a plugboard
enigma = EnigmaMachine([rotor1, rotor2, rotor3], reflector, plugboard)

# GUI Setup
root = tk.Tk()
root.title("Enigma Machine")
root.geometry("600x400")

style = ttk.Style()
style.configure("TLabel", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

input_label = ttk.Label(frame, text="Input Message:")
input_label.grid(row=0, column=0, sticky=tk.W)

input_text = tk.Text(frame, height=5, width=50, font=("Arial", 12))
input_text.grid(row=1, column=0, columnspan=3, pady=10)

rotor_frame = ttk.Frame(frame, padding="10")
rotor_frame.grid(row=2, column=0, columnspan=3)

rotor1_label = ttk.Label(rotor_frame, text="Rotor 1 Position (A-Z):")
rotor1_label.grid(row=0, column=0)
rotor1_entry = ttk.Entry(rotor_frame, width=3)
rotor1_entry.grid(row=0, column=1)

rotor2_label = ttk.Label(rotor_frame, text="Rotor 2 Position (A-Z):")
rotor2_label.grid(row=1, column=0)
rotor2_entry = ttk.Entry(rotor_frame, width=3)
rotor2_entry.grid(row=1, column=1)

rotor3_label = ttk.Label(rotor_frame, text="Rotor 3 Position (A-Z):")
rotor3_label.grid(row=2, column=0)
rotor3_entry = ttk.Entry(rotor_frame, width=3)
rotor3_entry.grid(row=2, column=1)

button_frame = ttk.Frame(frame)
button_frame.grid(row=3, column=0, columnspan=3, pady=10)

encode_button = ttk.Button(button_frame, text="Encode", command=lambda: on_encode_decode("encode"))
encode_button.grid(row=0, column=0, padx=5)

decode_button = ttk.Button(button_frame, text="Decode", command=lambda: on_encode_decode("decode"))
decode_button.grid(row=0, column=1, padx=5)

output_label = ttk.Label(frame, text="Output Message:")
output_label.grid(row=4, column=0, sticky=tk.W)

output_text = tk.Text(frame, height=5, width=50, font=("Arial", 12), state=tk.DISABLED)
output_text.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()
