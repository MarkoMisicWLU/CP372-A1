import socket


HOST = '127.0.0.1'  # Localhost address
PORT = 12349  #port number the server is listening on

def start_client():
    # creating a socket object for the client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    client.connect((HOST, PORT))  # connecting to the server

    # receive and print the first message to the server. 
    first_msg = client.recv(1024).decode()  
    print(first_msg)  
    
    # checking if the server is full before entering the chat loop
    while first_msg != 'Server is full. Try again later.':
        msg = input("You: ") # prompt user input
        client.send(msg.encode()) #send the message to the server
        
        if msg.lower() == "exit":  # check for "exit" or disconnect command
            break
        
        # receive and print the servers response
        response = client.recv(4096).decode()  
        print(f"Server: {response}")
    
    # lose the connection once the loop ends
    client.close()  

    # print a message indicating the connection has been ended. 
    if first_msg != 'Server is full. Try again later.':
        print("[DISCONNECTED] You have left the server.")
    else:
        print("[DISCONNECTED] Server is full")

if __name__ == "__main__":
    start_client()
