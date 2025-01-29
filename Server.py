import socket
import threading
import os
from datetime import datetime

# Server Configuration
HOST = '127.0.0.1'
PORT = 12349
MAX_CLIENTS = 3
FILE_REPOSITORY = os.getcwd() 

clients = {}
client_count = 0
client_label = 0
lock = threading.Lock()

def handle_client(conn, addr, client_name):
    global clients
    global client_count
    print(f"[NEW CONNECTION] {client_name} connected from {addr}")
    conn.send(f"Welcome {client_name}! Type your message or commands (status, list, exit).".encode())
    
    with lock:
        clients[client_name] = {'addr': addr, 'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'disconnected_at': None}
    
    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            
            if msg.lower() == "exit":
                print(f"[DISCONNECTING] {client_name} is disconnecting.")
                with lock:
                    clients[client_name]['disconnected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
            
            elif msg.lower() == "status":
                status_report = "\n".join([f"{k}: {v['addr']} | Connected: {v['connected_at']} | Disconnected: {v['disconnected_at']}" for k, v in clients.items()])
                conn.send(status_report.encode())
            
            elif msg.lower() == "list":
                files = os.listdir(FILE_REPOSITORY) if os.path.exists(FILE_REPOSITORY) else []
                conn.send("\n".join(files).encode() if files else "No files available.".encode())
            
            elif msg.startswith("get "):
                filename = msg[4:].strip()
                filepath = os.path.join(FILE_REPOSITORY, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        conn.sendall(f.read())
                else:
                    conn.send(f"File '{filename}' not found.".encode())
            
            else:
                conn.send(f"{msg}ACK".encode())
        except:
            break
    
    conn.close()
    with lock:
        clients[client_name]['disconnected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[DISCONNECTED] {client_name} from {addr}")
    client_count -= 1
    print(f"[ACTIVE CONNECTIONS] {client_count}")
def start_server():
    global client_count
    global client_label
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)
    print(f"[STARTED] Server is listening on {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        with lock:
            if client_count >= MAX_CLIENTS:
                conn.send("Server is full. Try again later.".encode())
                conn.close()
                continue
            client_count += 1
            client_label += 1
            client_name = f"Client{client_label:02d}"
        
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_name))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {client_count}")

if __name__ == "__main__":
    start_server()
