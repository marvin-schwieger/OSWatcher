import threading
import socket 

PORT = 5000
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

clients = set()
clients_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} Connected")
    print(conn, addr)
    
    while True:
        try:
            # Receive one message (up to 1024 bytes)
            msg = conn.recv(1024).decode(FORMAT)
            if msg:
                print(f"[{addr}] {msg}")
            else:
                print(f"[{addr}] No message received")
        except Exception as e:
            print(f"Error receiving message from {addr}: {e}")
        finally:
            # Remove client from set and close connection
            #with clients_lock:
            #    if conn in clients:
            #        clients.remove(conn)
            #conn.close()
            #print(f"[CONNECTION CLOSED] {addr}")
            print(clients)

def start():
    print('[SERVER STARTED]!')
    server = socket.create_server(ADDR, family=socket.AF_INET)
    server.listen()
    thread_count = 0
    while True:
        conn, addr = server.accept()
        
        with clients_lock:
            clients.add(addr)
            
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        thread_count += 1
        print(thread_count)

start()