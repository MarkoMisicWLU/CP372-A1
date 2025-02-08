import socket  # Import the socket module to enable network communication

# Define the server's IP address and port number
HOST = '127.0.0.1'  # Localhost address
PORT = 12349  # Port number the server is listening on

def start_client():
    # Create a socket object for the client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    client.connect((HOST, PORT))  # Connect to the server

    # Receive the first message from the server (e.g., a welcome message or a rejection)
    first_msg = client.recv(1024).decode()  
    print(first_msg)  
    
    # Check if the server is full before entering the chat loop
    while first_msg != 'Server is full. Try again later.':
        msg = input("You: ")  # Get user input
        client.send(msg.encode())  # Send the message to the server
        
        if msg.lower() == "exit":  # Check if the user wants to disconnect
            break
        
        # Receive and print the server's response
        response = client.recv(4096).decode()  
        print(f"Server: {response}")
    
    # Close the connection when the loop ends
    client.close()  

    # Print a message indicating disconnection
    if first_msg != 'Server is full. Try again later.':
        print("[DISCONNECTED] You have left the server.")
    else:
        print("[DISCONNECTED] Server is full")

# Run the client only if the script is executed directly
if __name__ == "__main__":
    start_client()
