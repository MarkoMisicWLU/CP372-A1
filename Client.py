import socket

HOST = '127.0.0.1'
PORT = 12346

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print(client.recv(1024).decode())  
    
    while True:
        msg = input("You: ")
        client.send(msg.encode())
        
        if msg.lower() == "exit":
            break
        
        response = client.recv(4096).decode()
        print(f"Server: {response}")
    
    client.close()
    print("[DISCONNECTED] You have left the chat.")

if __name__ == "__main__":
    start_client()