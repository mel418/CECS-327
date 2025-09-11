import socket
import threading
import time

def handle_client_tcp(client_socket, address):
    print(f"TCP connection from {address}")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"TCP received from {address}: {message}")
            response = f"Server received: {message}"
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f"TCP error with {address}: {e}")
    finally:
        client_socket.close()
        print(f"TCP connection with {address} closed")

def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 8001))
    server_socket.listen(5)
    print("TCP Server listening on port 8001...")
    
    while True:
        client_socket, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client_tcp, args=(client_socket, address))
        client_thread.start()

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 8002))
    print("UDP Server listening on port 8002...")
    
    while True:
        try:
            message, address = server_socket.recvfrom(1024)
            print(f"UDP received from {address}: {message.decode('utf-8')}")
            response = f"Server received: {message.decode('utf-8')}"
            server_socket.sendto(response.encode('utf-8'), address)
        except Exception as e:
            print(f"UDP error: {e}")

if __name__ == "__main__":
    print("Starting server...")
    
    # Start TCP server in a thread
    tcp_thread = threading.Thread(target=tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    # Start UDP server in a thread
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.daemon = True
    udp_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server shutting down...")