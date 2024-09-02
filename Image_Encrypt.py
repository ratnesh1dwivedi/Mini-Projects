import os
from tkinter import filedialog, messagebox, Tk, Label, Button, StringVar, OptionMenu
from PIL import Image, ImageTk
import numpy as np
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

# Module 1: Image Loader
def load_image(filepath):
    try:
        if not os.path.isfile(filepath):
            raise FileNotFoundError("The selected file does not exist.")
        
        image = Image.open(filepath).convert('RGB')
        return np.array(image), image
    except Exception as e:
        messagebox.showerror("Error", f"Error loading image: {e}")
        return None, None

# Module 2: Secure Key Management
def generate_key(password, salt=None):
    try:
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    except Exception as e:
        messagebox.showerror("Error", f"Error generating key: {e}")
        return None, None

def save_key(key, filepath):
    try:
        with open(filepath, 'wb') as f:
            f.write(key)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving key: {e}")

def load_key(filepath):
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Error loading key: {e}")
        return None

# Module 3: Advanced Pixel Manipulation
def encrypt_image(image, key, method="scramble"):
    try:
        if method == "scramble":
            return scramble_encrypt(image, key)
        elif method == "aes":
            return aes_encrypt(image, key)
        else:
            raise ValueError("Unsupported encryption method")
    except Exception as e:
        messagebox.showerror("Error", f"Error during encryption: {e}")
        return None

def decrypt_image(image, key, method="scramble"):
    try:
        if method == "scramble":
            return scramble_decrypt(image, key)
        elif method == "aes":
            return aes_decrypt(image, key)
        else:
            raise ValueError("Unsupported decryption method")
    except Exception as e:
        messagebox.showerror("Error", f"Error during decryption: {e}")
        return None

def scramble_encrypt(image, key):
    try:
        np.random.seed(int.from_bytes(key[:4], 'little'))
        indices = np.arange(image.size)
        np.random.shuffle(indices)
        encrypted_image = image.flatten()[indices].reshape(image.shape)
        return encrypted_image
    except Exception as e:
        messagebox.showerror("Error", f"Error in scrambling encryption: {e}")
        return None

def scramble_decrypt(image, key):
    try:
        np.random.seed(int.from_bytes(key[:4], 'little'))
        indices = np.arange(image.size)
        np.random.shuffle(indices)
        decrypted_image = np.empty_like(image.flatten())
        decrypted_image[indices] = image.flatten()
        return decrypted_image.reshape(image.shape)
    except Exception as e:
        messagebox.showerror("Error", f"Error in scrambling decryption: {e}")
        return None

def aes_encrypt(image, key):
    try:
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_image = pad_image(image)
        encrypted_image = encryptor.update(padded_image.tobytes()) + encryptor.finalize()
        return np.frombuffer(encrypted_image, dtype=np.uint8).reshape(padded_image.shape)
    except Exception as e:
        messagebox.showerror("Error", f"Error in AES encryption: {e}")
        return None

def aes_decrypt(image, key):
    try:
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_image = decryptor.update(image.tobytes()) + decryptor.finalize()
        return np.frombuffer(decrypted_image, dtype=np.uint8).reshape(image.shape)
    except Exception as e:
        messagebox.showerror("Error", f"Error in AES decryption: {e}")
        return None

def pad_image(image):
    """ Pads image data to be a multiple of 16 bytes for AES """
    try:
        h, w, c = image.shape
        pad_h = (16 - h % 16) if h % 16 != 0 else 0
        pad_w = (16 - w % 16) if w % 16 != 0 else 0
        return np.pad(image, ((0, pad_h), (0, pad_w), (0, 0)), 'constant')
    except Exception as e:
        messagebox.showerror("Error", f"Error in padding image: {e}")
        return None

# Module 4: File Management
def save_image(image, output_path):
    try:
        im = Image.fromarray(image)
        im.save(output_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving image: {e}")

# Module 5: GUI Implementation
class ImageEncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Encryption Tool")
        self.root.geometry("500x650")
        
        self.image = None
        self.processed_image = None
        self.key = None
        self.method = StringVar(root)
        self.method.set("scramble")
        self.image_path = StringVar(root)

        # Layout
        Label(root, text="Image Encryption Tool", font=("Helvetica", 16)).pack(pady=10)

        self.image_label = Label(root)
        self.image_label.pack(pady=10)

        self.path_label = Label(root, textvariable=self.image_path, font=("Helvetica", 10))
        self.path_label.pack(pady=5)
        
        Button(root, text="Load Image", command=self.load_image).pack(pady=5)
        Button(root, text="Generate Key", command=self.generate_key).pack(pady=5)
        Button(root, text="Load Key", command=self.load_key).pack(pady=5)
        
        Label(root, text="Select Method:").pack(pady=5)
        OptionMenu(root, self.method, "scramble", "aes").pack(pady=5)
        
        Button(root, text="Encrypt Image", command=self.encrypt_image).pack(pady=5)
        Button(root, text="Decrypt Image", command=self.decrypt_image).pack(pady=5)
        Button(root, text="Save Image", command=self.save_image).pack(pady=20)
    
    def load_image(self):
        filepath = filedialog.askopenfilename(
            title="Select Image", 
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
        )
        if filepath:
            self.image_path.set(f"Loaded Image: {os.path.basename(filepath)}")
            np_image, pil_image = load_image(filepath)
            if np_image is not None:
                self.image = np_image
                self.display_image(pil_image)
                messagebox.showinfo("Success", "Image loaded successfully.")
            else:
                messagebox.showerror("Error", "Failed to load the image.")
        else:
            messagebox.showwarning("Warning", "No image selected.")

    def display_image(self, pil_image):
        pil_image.thumbnail((400, 400))  # Resize for display
        tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

    def generate_key(self):
        password = simpledialog.askstring("Password", "Enter a password for key generation:", show='*')
        if password:
            key, salt = generate_key(password)
            if key is not None:
                self.key = key
                messagebox.showinfo("Success", "Key generated successfully.")

    def load_key(self):
        filepath = filedialog.askopenfilename(
            title="Select Key File", 
            filetypes=[("Key Files", "*.key"), ("All Files", "*.*")]
        )
        if filepath:
            self.key = load_key(filepath)
            if self.key is not None:
                messagebox.showinfo("Success", "Key loaded successfully.")
    
    def encrypt_image(self):
        if self.image is None:
            messagebox.showwarning("Warning", "Please load an image first.")
            return
        if self.key is None:
            messagebox.showwarning("Warning", "Please generate or load a key first.")
            return
        method = self.method.get()
        encrypted_image = encrypt_image(self.image, self.key, method)
        if encrypted_image is not None:
            self.processed_image = encrypted_image
            self.display_image(Image.fromarray(encrypted_image))
            messagebox.showinfo("Success", "Image encrypted successfully.")

    def decrypt_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "Please encrypt an image first.")
            return
        if self.key is None:
            messagebox.showwarning("Warning", "Please generate or load a key first.")
            return
        method = self.method.get()
        decrypted_image = decrypt_image(self.processed_image, self.key, method)
        if decrypted_image is not None:
            self.display_image(Image.fromarray(decrypted_image))
            messagebox.showinfo("Success", "Image decrypted successfully.")

    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No image to save.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filepath:
            save_image(self.processed_image, filepath)
            messagebox.showinfo("Success", "Image saved successfully.")

if __name__ == "__main__":
    root = Tk()
    app = ImageEncryptionApp(root)
    root.mainloop()
