import socket
import sys
import os

def main():
    # get server identifier from env variable
    server_id = os.environ.get('SERVER_ID', 'unknown')
    host = '0.0.0.0' # listen on all network interfaces
    port = 5000

    # create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # allow address reuse (important for Docker)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind to address and port
    server_socket.bind((host, port))

    # listen for incoming connections (max 5 queued connections)
    server_socket.listen(5)
    print(f"Server {server_id} ready on port {port}")

    try:
        while True:
            # accept incoming connection
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            # send response with server identifier
            message = f"Hello from {server_id}\n"
            client_socket.send(message.encode('utf-8'))
            print(f"Sent: {message.strip()}")

            # close connection 
            client_socket.close()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()