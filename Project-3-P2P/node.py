from flask import Flask, jsonify, request
import uuid
import os
import threading
import time
import sys
import requests

app = Flask(__name__)

# Force unbuffered output for Docker logs
sys.stdout.flush()

# generate unique identifier for this node
node_id = str(uuid.uuid4())

# get port from env variable for Docker
port = int(os.getenv('PORT', 5000))

bootstrap_url = os.getenv('BOOTSTRAP_URL', 'http://bootstrap:5000')

node_url = os.getenv('NODE_URL', f'http://localhost:{port}')

# store known peers - using set to avoid duplicates
peers = set()

# lock for thread-safe operations
peers_lock = threading.Lock()

def register_with_bootstrap():
    '''Register this node with the bootstrap server'''
    try:
        response = requests.post(
            f'{bootstrap_url}/register',
            json={'peer_url': node_url},
            timeout=5
        )
        if response.status_code == 200:
            print(f"[{node_id}] Successfully registered with bootstrap")
            return True
        else:
            print(f"[{node_id}] Failed to register: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{node_id}] Error registering with bootstrap: {e}")
        return False
    
def discover_peers():
    '''Get peer list from bootstrap node'''
    try:
        response = requests.get(f'{bootstrap_url}/peers', timeout=5)
        if response.status_code == 200:
            peer_list = response.json().get('peers', [])

            with peers_lock:
                for peer in peer_list:
                    # dont add ourselves
                    if peer != node_url:
                        peers.add(peer)
            
            print(f"[{node_id}] Discovered {len(peers)} peers")
            return True
    except Exception as e:
        print(f"[{node_id}] Error discovering peers: {e}")
        return False

def peer_discovery_loop():
    '''Periodically update peer list'''
    # wait a bit for node to start
    time.sleep(5)

    # register with bootstrap
    register_with_bootstrap()

    #intiial peer discovery
    discover_peers()

    #periodic updates every 30 secs
    while True:
        time.sleep(30)
        discover_peers()

@app.route('/')
def home():
    '''Basic endpoint to verify node is running'''
    return jsonify({
        "message": f"Node {node_id} is running!",
        "node_id": node_id,
        "peer_count": len(peers)
    })

@app.route('/message', methods=['POST'])
def receive_message():
    '''
    Receive a message from another peer
    Expected JSON: {"sender": "node_id", "msg": "Hello!"}
    '''
    data = request.get_json()
    sender = data.get('sender')
    message = data.get('msg')

    print(f"[{node_id}] Received message from {sender}: {message}", flush=True)

    return jsonify({"status": "received"}), 200

@app.route('/peers', methods=['GET'])
def get_peers():
    '''Return list of known peers'''
    with peers_lock:
        peer_list = list(peers)
    
    return jsonify({
        "node_id": node_id,
        "peers": peer_list
    })

@app.route('/broadcast', methods=['POST'])
def broadcast_message():
    '''Send a message to all known peers'''
    data = request.get_json()
    message = data.get('msg', 'Hello from ' + node_id)

    with peers_lock:
        peer_list = list(peers)
    
    results = []
    for peer in peer_list:
        try:
            response = requests.post(
                f'{peer}/message',
                json={'sender': node_id, 'msg': message},
                timeout=5
            )
            results.append({
                "peer": peer,
                "status": "sent",
                "response": response.status_code
            })
        except Exception as e:
            results.append({
                "peer": peer,
                "status": "failed",
                "error": str(e)
            })

    return jsonify({
        "broadcast_results": results,
        "total_peers": len(peer_list)
    })


if __name__ == '__main__':
    # start peer discovery in backgroun thread
    discovery_thread = threading.Thread(target=peer_discovery_loop, daemon=True)
    discovery_thread.start()
    
    print(f"Starting node {node_id} on port {port}", flush=True)
    # 0.0.0.0 allows external connections (important for Docker)
    app.run(host='0.0.0.0', port=port, debug=True)