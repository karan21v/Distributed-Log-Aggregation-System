import socket
import time
import random
from cryptography.fernet import Fernet   

# LOAD KEY
with open("key.txt", "rb") as f:         
    key = f.read().strip()
cipher = Fernet(key)                    

SERVER_IP = "10.247.237.226"
PORT = 9000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

machine_id = "server" + str(random.randint(1,5))

while True:

    timestamp = time.time()

    log_levels = ["INFO", "WARN", "ERROR"]
    level = random.choice(log_levels)

    messages = [
        "User login",
        "File uploaded",
        "Database query",
        "Connection closed",
        "Disk usage high"
    ]

    message = random.choice(messages)

    log = f"{timestamp} | {machine_id} | {level} | {message}"
# ENCRYPTION
    encrypted = cipher.encrypt(log.encode())
    client_socket.sendto(encrypted, (SERVER_IP, PORT))

    print("Sent:", log)

    time.sleep(1)