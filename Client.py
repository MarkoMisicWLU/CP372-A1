import socket

HOST = '127.0.0.1'
PORT = 12349

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    first_msg = client.recv(1024).decode()
    print(first_msg)  
    
    while first_msg != 'Server is full. Try again later.':
        msg = input("You: ")
        client.send(msg.encode())
        
        if msg.lower() == "exit":
            break
        
        response = client.recv(4096).decode()
        print(f"Server: {response}")
    
    client.close()
    if first_msg != 'Server is full. Try again later.':
        print("[DISCONNECTED] You have left the server.")
    else:
        print("[DISCONNECTED] Server is full")

if __name__ == "__main__":
    start_client()