from flask import Flask, jsonify, request, send_from_directory
import uuid
import os
import threading
import time
import sys
import requests
import hashlib

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

# Phase 1: File Storage
STORAGE_DIR = './storage'
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    '''upload a file to this node's storage'''
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    filepath = os.path.join(STORAGE_DIR, file.filename)
    file.save(filepath)

    print(f"[{node_id}] File uploaded: {file.filename}", flush=True)

    return jsonify({
        "status": "uploaded",
        "filename": file.filename,
        "node_id": node_id
    }), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    '''Download a file from this node's storage'''
    try:
        return send_from_directory(STORAGE_DIR, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    
@app.route('/files', methods=['GET'])
def list_files():
    '''list all files stored on this node'''
    try:
        files = os.listdir(STORAGE_DIR)
        return jsonify({
            "node_id": node_id,
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Phase 2: key-balue store
kv_store = {}
kv_lock = threading.Lock()

# Phase 3: DHT routing
def hash_key(key):
    '''WHERE does data go? (determine storage location)'''
    hash_obj = hashlib.sha1(key.encode('utf-8'))
    hash_bytes = hash_obj.digest()[:8] # take first 8 bytes of hash to convert to int
    return int.from_bytes(hash_bytes, byteorder='big')

def hash_node(node_url):
    '''Hash a node URL to determine its position in the DHT ring'''
    hash_obj = hashlib.sha1(node_url.encode('utf-8'))
    hash_bytes = hash_obj.digest()[:8]
    return int.from_bytes(hash_bytes, byteorder='big')

def get_responsible_node(key):
    '''WHO stores this?'''
    key_hash = hash_key(key)

    with peers_lock:
        peer_list = list(peers)
        peer_list.append(node_url) # include ourselves in list
    
    if not peer_list:
        return node_url # if no peers, we're responsible
    
    # create list of (node_url, node_hash) tuples and sort by hash
    node_hashes = [(node, hash_node(node)) for node in peer_list]
    node_hashes.sort(key=lambda x: x[1])

    # find first node whose hash is >= key_hash (clockwise)
    for node, node_hash in node_hashes:
        if node_hash >= key_hash:
            return node
    
    # if no node >= key_hash, wrap around to first node
    return node_hashes[0][0]

@app.route('/kv', methods=['POST'])
def store_kv():
    '''Store a key-value pair using DHT routing'''
    data = request.get_json()

    if not data or 'key' not in data or 'value' not in data:
        return jsonify({"error": "Missing key or value"}), 400
    
    key = data['key']
    value = data['value']

    responsible_node = get_responsible_node(key)

    if responsible_node != node_url:
        print(f"[{node_id}] Forwarding '{key}' to {responsible_node}", flush=True)
        try:
            response = requests.post(
                f"{responsible_node}/kv",
                json={"key": key, "value": value},
                timeout=5
            )
            result = response.json()
            result["forwarded_from"] = node_id
            return jsonify(result), response.status_code
        except Exception as e:
            return jsonify({"error": f"Failed to forward: {str(e)}"}), 500
        
    with kv_lock:
        kv_store[key] = value
    
    print(f"[{node_id}] Stored KV: {key} = {value}", flush=True)

    return jsonify({
        "status": "stored",
        "key": key,
        "value": value,
        "node_id": node_id,
        "responsible_node": responsible_node
    }), 200

@app.route('/kv/<key>', methods=['GET'])
def get_kv(key):
    '''Retrieve a value by key using DHT routing'''
    responsible_node = get_responsible_node(key)

    if responsible_node != node_url:
        print(f"[{node_id}] Forwarding query for '{key} to {responsible_node}", flush=True)
        try:
            response = requests.get(
                f"{responsible_node}/kv/{key}",
                timeout=5
            )
            result = response.json()
            result["forwarded_from"] = node_id
            return jsonify(result), response.status_code
        except Exception as e:
            return jsonify({"error": f"Failed to forward: {str(e)}"})
        
    with kv_lock:
        value = kv_store.get(key)

    if value is None:
        return jsonify({"error": "Key not found"}), 404
    
    print(f"[{node_id}] Retrieved KV: {key} = {value}", flush=True)

    return jsonify({
        "key": key,
        "value": value,
        "node_id": node_id,
        "responsible_node": responsible_node
    }), 200

@app.route('/kv', methods=['GET'])
def list_kv():
    '''List all key-value pairs stored locally on this node'''
    with kv_lock:
        store_copy = dict(kv_store)

    return jsonify({
        "node_id": node_id,
        "store": store_copy,
        "count": len(store_copy)
    })

@app.route('/kv/debug', methods=['GET'])
def debug_dht():
    with peers_lock:
        peer_list = list(peers)
        peer_list.append(node_url)

    node_info = []
    for peer in sorted(peer_list):
        node_info.append({
            "url": peer,
            "hash": hash_node(peer),
            "is_me": peer == node_url
        })
    
    with kv_lock:
        key_info = []
        for key in kv_store.keys():
            key_info.append({
                "key": key,
                "hash": hash_key(key),
                "responsible_node": get_responsible_node(key)
            })

    return jsonify({
        "nodes": node_info,
        "local_keys": key_info,
        "total_nodes": len(peer_list)
    })

# P2P Infrastructure

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
        "peer_count": len(peers),
        "stored_keys": len(kv_store),
        "stored_files": len(os.listdir(STORAGE_DIR))
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