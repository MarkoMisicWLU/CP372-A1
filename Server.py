import socket  # Import the socket module to enable network communication
import threading  # Import threading for handling multiple clients concurrently
import os  # Import os for file system operations
from datetime import datetime  # Import datetime to log connection timestamps

# Server Configuration
HOST = '127.0.0.1'  # Localhost IP address
PORT = 12349  # Port number for the server to listen on
MAX_CLIENTS = 3  # Maximum number of concurrent clients allowed
FILE_REPOSITORY = os.getcwd()  # Directory for file storage (current working directory)

# Global variables for managing clients
clients = {}  # Dictionary to store client connection details
client_count = 0  # Counter for active clients
client_label = 0  # Counter for labeling clients
lock = threading.Lock()  # Thread lock for synchronizing shared resources

def handle_client(conn, addr, client_name):
    """
    Handles communication with a connected client.
    """
    global clients
    global client_count

    print(f"[NEW CONNECTION] {client_name} connected from {addr}")
    
    # Send a welcome message to the client
    conn.send(f"Welcome {client_name}! Type your message or commands (status, list, exit).".encode())

    # Store client connection details
    with lock:
        clients[client_name] = {
            'addr': addr,
            'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'disconnected_at': None
        }

    list_mode = False  # Flag to track whether the client is selecting a file for download

    while True:
        try:
            # Receive and decode client message
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break  # If message is empty, disconnect the client
            
            if msg.lower() == "exit":
                # Handle client exit request
                print(f"[DISCONNECTING] {client_name} is disconnecting.")
                with lock:
                    clients[client_name]['disconnected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
            
            elif msg.lower() == "status":
                # Send the status of all connected clients
                status_report = "\n".join([
                    f"{k}: {v['addr']} | Connected: {v['connected_at']} | Disconnected: {v['disconnected_at']}"
                    for k, v in clients.items()
                ])
                conn.send(status_report.encode())

            elif msg.lower() == "list":
                # Send a list of files available in the repository
                files = os.listdir(FILE_REPOSITORY) if os.path.exists(FILE_REPOSITORY) else []
                if files:
                    conn.send(("\n".join(files) + "\nEnter the file name to download:").encode())
                    list_mode = True  # Enable file selection mode
                else:
                    conn.send("No files available.".encode())

            elif list_mode:
                # Handle file download request
                filename = msg
                filepath = os.path.join(FILE_REPOSITORY, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        conn.sendall(f.read())  # Send file contents
                else:
                    conn.send(f"File '{filename}' not found.".encode())
                list_mode = False  # Reset file selection mode
            
            else:
                # Echo back the received message with an acknowledgment
                conn.send(f"{msg}ACK".encode())
        except:
            break  # Handle any connection errors by breaking the loop

    # Close the connection when the client disconnects
    conn.close()

    # Update client disconnection time
    with lock:
        clients[client_name]['disconnected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"[DISCONNECTED] {client_name} from {addr}")

    # Reduce active client count
    global client_count
    client_count -= 1
    print(f"[ACTIVE CONNECTIONS] {client_count}")


def start_server():
    """
    Starts the server and listens for incoming client connections.
    """
    global client_count
    global client_label

    # Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))  # Bind the socket to the address and port
    server.listen(MAX_CLIENTS)  # Start listening for incoming connections

    print(f"[STARTED] Server is listening on {HOST}:{PORT}")

    while True:
        # Accept a new client connection
        conn, addr = server.accept()
        
        with lock:
            if client_count >= MAX_CLIENTS:
                # Reject connection if the server is full
                conn.send("Server is full. Try again later.".encode())
                conn.close()
                continue  # Skip to the next connection attempt
            
            # Increment client count and assign a unique label
            client_count += 1
            client_label += 1
            client_name = f"Client{client_label:02d}"  # Format as Client01, Client02, etc.
        
        # Create a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_name))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {client_count}")

# Run the server only if the script is executed directly
if __name__ == "__main__":
    start_server()
