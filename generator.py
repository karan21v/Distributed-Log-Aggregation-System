import socket, time, random, threading
from cryptography.fernet import Fernet

# LOAD KEY
with open("key.txt", "rb") as f:
    key = f.read().strip()
cipher = Fernet(key)

SERVER_IP = "127.0.0.1"
PORT = 9000

NUM_MACHINES = 300      #  increase for drops
SEND_DELAY = 0.0005        #  decrease for drops

# MESSAGES

user_events = [
    "User login",
    "User logout",
    "Password changed"
]

system_events = [
    "CPU usage high",
    "Disk usage high",
    "Service restarted"
]

db_events = [
    "Database query executed",
    "Transaction committed",
    "Connection pool exhausted"
]

network_events = [
    "Connection established",
    "Connection closed",
    "Packet timeout"
]

all_categories = [user_events, system_events, db_events, network_events]


def generate_logs(machine_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        timestamp = time.time()

        # keep your logic
        lvl = "ERROR" if random.random() < 0.15 else random.choice(["INFO", "WARN", "ERROR"])

        # improved message selection
        category = random.choice(all_categories)
        message = random.choice(category)

        log = f"{timestamp} | server{machine_id} | {lvl} | {message}"

        encrypted = cipher.encrypt(log.encode())
        sock.sendto(encrypted, (SERVER_IP, PORT))

        print("Sent:", log)

        time.sleep(SEND_DELAY)


# THREADS
for i in range(NUM_MACHINES):
    threading.Thread(target=generate_logs, args=(i+1,), daemon=True).start()

while True:
    time.sleep(1)