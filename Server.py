import socket 
import threading  
import os  
from datetime import datetime

HOST = '127.0.0.1' 
PORT = 12349  
MAX_CLIENTS = 3  # max number of concurrent clients allowed
FILE_REPOSITORY = os.getcwd()  # directory for file storage (current working directory)


clients = {}  # dictionary to store client connection details
client_count = 0  # counter for active clients
client_label = 0  # counter for labeling clients
lock = threading.Lock()  # thread lock for synchronizing shared resources

def handle_client(conn, addr, client_name):
    """
    Handles communication with a connected client.
    """
    global clients
    global client_count

    print(f"[NEW CONNECTION] {client_name} connected from {addr}")
    
    #greet the client with a welcome message once they've connected. 
    conn.send(f"Welcome {client_name}! Type your message or commands (status, list, exit).".encode())

    # store the client connection details in the 
    with lock:
        clients[client_name] = {
            'addr': addr,
            'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'disconnected_at': None
        }

    list_mode = False  # track whether a client is selecting a file for download

    while True:
        try:
            # receive and decode the client message
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break  #if message is empty, disconnect the client
            
            if msg.lower() == "exit":
                # disconnect if the client enters the "exit" command
                print(f"[DISCONNECTING] {client_name} is disconnecting.")
                with lock:
                    clients[client_name]['disconnected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
            
            elif msg.lower() == "status":
                # output the status of all connected clients
                status_report = "\n".join([
                    f"{k}: {v['addr']} | Connected: {v['connected_at']} | Disconnected: {v['disconnected_at']}"
                    for k, v in clients.items()
                ])
                conn.send(status_report.encode())

            elif msg.lower() == "list":
                # show a list of files available in the repo
                files = os.listdir(FILE_REPOSITORY) if os.path.exists(FILE_REPOSITORY) else []
                if files:
                    conn.send(("\n".join(files) + "\nEnter the file name to download:").encode())
                    list_mode = True  # update the file selection flag
                else:
                    conn.send("No files available.".encode())

            elif list_mode:
                # handling file content output 
                filename = msg
                filepath = os.path.join(FILE_REPOSITORY, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        conn.sendall(f.read())  # send contents of the requested file
                else:
                    conn.send(f"File '{filename}' not found.".encode())
                list_mode = False  # reset the flag
            
            else:
                # echo the received message with an acknowledgement
                conn.send(f"{msg}ACK".encode())
        except:
            break  # break the loop upon connection error

    conn.close()

    # update the client disconnection time
    with lock:
        clients[client_name]['disconnected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"[DISCONNECTED] {client_name} from {addr}")

    # decrease client count
    global client_count
    client_count -= 1
    print(f"[ACTIVE CONNECTIONS] {client_count}")


def start_server():
    """
    Starts the server and listens for incoming client connections.
    """
    global client_count
    global client_label

    # create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))  # bind the socket to the address and port
    server.listen(MAX_CLIENTS)  # start listening for incoming connections

    print(f"[STARTED] Server is listening on {HOST}:{PORT}")

    while True:
        # accept a new client connection
        conn, addr = server.accept()
        
        with lock:
            if client_count >= MAX_CLIENTS:
                # check if the server if full before accepting a new connection
                conn.send("Server is full. Try again later.".encode())
                conn.close()
                continue 
            
            # increase the client count and assign a new identifier
            client_count += 1
            client_label += 1
            client_name = f"Client{client_label:02d}" 
        
        # start a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_name))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {client_count}")


if __name__ == "__main__":
    start_server()
