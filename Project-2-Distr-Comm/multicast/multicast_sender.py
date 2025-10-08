import socket
import time
import json
import random
import os

def main():
    MULTICAST_GROUP = '224.1.1.1'
    PORT= 5007
    sender_id = os.environ.get('SENDER_ID', 'sender')

    # create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # sett TTL (time-to-live) for multicast packets
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    print(f"{sender_id} sending to {MULTICAST_GROUP}:{PORT}")

    try:
        count = 0
        while True:
            # send different typesd of messages
            if count % 3 == 0:
                # send plain text
                message = f"Multicast message {count} from {sender_id}"
                sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
                print(f"Send text: {message}")

            elif count % 3 == 1:
                # send JSON data
                data =  {
                    "sender": sender_id, 
                    "sensor": "temperature",
                    "value": round(20 + random.random() * 10, 2),
                    "timestamp": time.time()
                } 
                message = json.dumps(data)
                sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
                print(f"Sent JSON: {message}")
            
            else:
                # send binary data
                binary_data = bytes([random.randint(0, 255) for _ in range(10)])
                sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
                print(f"Sent binary: {binary_data.hex()}")

            count += 1
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping sender")
    finally:
        sock.close()

if __name__ == "__main__":
    main()