import socket
import struct
import argparse
import time
import json

def main():
    parser = argparse.ArgumentParser(description='Multicast UDP Receiver')
    parser.add_argument('--duration', type=int, default=60, help='Duration to listen (seconds)')
    args = parser.parse_args()

    # multicast config
    MULTICAST_GROUP = '224.1.1.1'
    PORT = 5007

    # create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # allow multiple listeners on same port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind to port (not specific to multicast address)
    sock.bind(('', PORT))

    # tell the kernel to add this socket to multicast group
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Joined multicast group {MULTICAST_GROUP}:{PORT}")

    start_time = time.time()

    try:
        while time.time() - start_time < args.duration:
            # set timeout to check duration
            sock.settimeout(1.0)

            try:
                data, address = sock.recvfrom(1024)

                # try to decode as JSON
                try:
                    message = json.loads(data.decode('utf-8'))
                    print(f"Received JSON: {message} from {address}")
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # handle as binary or plain text
                    try:
                        message = data.decode('utf-8')
                        print(f"Received text: {message.strip()} from {address}")
                    except UnicodeDecodeError:
                        print(f"Received binary: {data.hex()} from {address}")
            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        print("Leaving multicast group")
        sock.close()

if __name__ == "__main__":
    main()