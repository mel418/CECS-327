import socket
import sys

def main():
    # server hostname (Docker service name)
    host = 'server' # this will resolve to oe of the the server containers
    port = 5000

    # create TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to server
        client_socket.connect((host, port))

        # receive response (up to 1024 bytes)
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {response.strip()}")

    except socket.error as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
        