import threading
import socket 
import json

# Get actual IP address by connecting to a public DNS server
# This is a workaround to avoid getting VirtualBox host-only IP 
def get_actual_ip() -> str:

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

PORT = 5000
SERVER = get_actual_ip()
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
FILE = "test..."

clients = set() # Set stores unique client addresses
clients_lock = threading.Lock()


def handle_client(conn, addr) -> None:
    print(f"[NEW CONNECTION] {addr} connected.")
    
    while True:
        # Receive one message (up to 1024 bytes)
        msg = conn.recv(1024).decode(FORMAT)
        print(type(msg))
        if msg:
            print(f"[{addr}] {msg}")
            conn.send("[SUCCESS]".encode(FORMAT)) 
        else:
            print(f"[{addr}] No message received!")
            break
        
        msg_decoded = json.loads(msg)
        print(type(msg_decoded))
        # here it shall write information from clients into one file
        with clients_lock:
            print("check")
            if addr not in clients:
                clients.add(addr)

def start() -> None:
    print("[SERVER STARTED]", SERVER)
    server = socket.create_server(ADDR, family=socket.AF_INET)
    server.listen()
    while True:
        
        conn, addr = server.accept()

        #with clients_lock:
        #    clients.add(addr)
            
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()