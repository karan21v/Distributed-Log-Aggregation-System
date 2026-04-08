import tkinter as tk
from tkinter import ttk
import socket
import time
from cryptography.fernet import Fernet

# LOAD KEY
try:
    with open("key.txt", "rb") as f:
        key = f.read().strip()
    cipher = Fernet(key)
except FileNotFoundError:
    print("[ERROR] 'key.txt' not found!")
    exit()

# NETWORK CONFIG
SERVER_IP = "10.247.237.226"  
PORT = 9000
MACHINE_ID = "VIVA_DEMO_NODE"

# THEME
BG_MAIN = "#0d1117"
BG_CARD = "#161b22"
ACCENT_BLUE = "#58a6ff"
ACCENT_GREEN = "#238636"
TEXT_MAIN = "#c9d1d9"

class VisualClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Live UDP Sender")
        self.root.geometry("550x450")
        self.root.configure(bg=BG_MAIN)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Terminal Client", font=("Segoe UI", 16, "bold"), fg=ACCENT_BLUE, bg=BG_MAIN).pack(pady=15)

        # Input Frame
        input_frame = tk.Frame(self.root, bg=BG_CARD, bd=1, relief="ridge", padx=20, pady=20)
        input_frame.pack(fill="x", padx=20)

        # SEVERITY LEVEL SELECTOR 
        level_frame = tk.Frame(input_frame, bg=BG_CARD)
        level_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(level_frame, text="Severity Level:", font=("Segoe UI", 10, "bold"), fg="white", bg=BG_CARD).pack(side="left")
        self.level_var = tk.StringVar(value="ERROR")
        level_menu = ttk.Combobox(level_frame, textvariable=self.level_var, values=["INFO", "WARN", "ERROR"], state="readonly", width=10)
        level_menu.pack(side="left", padx=10)

        # CUSTOM MESSAGE INPUT
        tk.Label(input_frame, text="Enter Custom Log Message:", font=("Segoe UI", 10, "bold"), fg="white", bg=BG_CARD).pack(anchor="w")
        
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(input_frame, textvariable=self.entry_var, font=("Consolas", 12), bg="#21262d", fg="white", insertbackground="white")
        self.entry.pack(fill="x", pady=10)
        
        self.root.bind('<Return>', lambda event: self.send_packet())

        self.send_btn = tk.Button(input_frame, text="SEND SECURE DATAGRAM", command=self.send_packet, bg=ACCENT_GREEN, fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=5)
        self.send_btn.pack(fill="x", pady=5)

        # TRANSMISSION OUTPUT CONSOLE
        output_frame = tk.Frame(self.root, bg=BG_CARD, bd=1, relief="ridge", padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(output_frame, text="Transmission Output", font=("Segoe UI", 10, "bold"), fg="#8b949e", bg=BG_CARD).pack(anchor="w")
        
        self.output_box = tk.Text(output_frame, font=("Consolas", 9), bg="#000000", fg=TEXT_MAIN, bd=1, relief="sunken", height=8)
        self.output_box.pack(fill="both", expand=True, pady=5)

        # HIGH CONTRAST HACKER TERMINAL COLORS
        self.output_box.tag_config("status", foreground="#58a6ff")       # Bright Blue
        self.output_box.tag_config("raw", foreground="#ffffff")          # Pure White
        self.output_box.tag_config("aes", foreground="#ff72e4")          # Neon Magenta (Very visible)
        self.output_box.tag_config("success", foreground="#3fb950")      # Bright Lime Green
        self.output_box.tag_config("error", foreground="#ff7b72")        # Bright Red

    def send_packet(self):
        custom_message = self.entry_var.get().strip()
        if not custom_message:
            return

        timestamp = time.time()
        selected_level = self.level_var.get()
        log_string = f"{timestamp} | {MACHINE_ID} | {selected_level} | {custom_message}"

        self.send_btn.config(state="disabled", bg="#21262d")
        
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "[SYSTEM] ENCRYPTING PAYLOAD...\n", "status")
        self.output_box.insert(tk.END, f"[RAW] {log_string}\n", "raw")
        self.root.update()
        time.sleep(0.1) 

        try:
            encrypted_payload = cipher.encrypt(log_string.encode('utf-8'))
            self.sock.sendto(encrypted_payload, (SERVER_IP, PORT))
            
            display_hash = str(encrypted_payload[:45]) + "...[TRUNC]"
            self.output_box.insert(tk.END, f"[AES] {display_hash}\n", "aes")
            self.output_box.insert(tk.END, "[OK] UDP DATAGRAM TRANSMITTED\n", "success")
            
            self.entry_var.set("") 
            
        except Exception as e:
            self.output_box.insert(tk.END, f"[FAIL] TRANSMISSION ERROR: {e}\n", "error")

        self.root.after(1500, self.reset_ui)

    def reset_ui(self):
        self.send_btn.config(state="normal", bg=ACCENT_GREEN)

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualClient(root)
    root.mainloop()