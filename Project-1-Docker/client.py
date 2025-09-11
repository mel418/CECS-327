import socket
import time
import sys

def tcp_client(server_host, client_id):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, 8001))
        
        for i in range(3):
            message = f"Hello from TCP client {client_id}, message {i+1}"
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(f"TCP Client {client_id} received: {response}")
            time.sleep(2)
            
        client_socket.close()
    except Exception as e:
        print(f"TCP Client {client_id} error: {e}")

def udp_client(server_host, client_id):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        for i in range(3):
            message = f"Hello from UDP client {client_id}, message {i+1}"
            client_socket.sendto(message.encode('utf-8'), (server_host, 8002))
            response, address = client_socket.recvfrom(1024)
            print(f"UDP Client {client_id} received: {response.decode('utf-8')}")
            time.sleep(2)
            
        client_socket.close()
    except Exception as e:
        print(f"UDP Client {client_id} error: {e}")

if __name__ == "__main__":
    client_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    server_host = "server"  # Docker service name
    
    print(f"Starting client {client_id}...")
    
    # Test TCP
    print(f"Client {client_id} testing TCP...")
    tcp_client(server_host, client_id)
    
    # Test UDP
    print(f"Client {client_id} testing UDP...")
    udp_client(server_host, client_id)
    
    print(f"Client {client_id} finished")