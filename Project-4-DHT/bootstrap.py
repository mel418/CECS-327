from flask import Flask, request, jsonify
import threading
app = Flask(__name__)

# registry of all peers
peer_registry = set()
registry_lock = threading.Lock()

@app.route('/')
def home():
    '''Bootstrap node status'''
    return jsonify({
        "message": "Bootstrap node running",
        "registered_peers": len(peer_registry)
    })

@app.route('/register', methods=['POST'])
def register():
    '''
    Register a new peer with the bootstrap node
    Expected JSON: {"peer_url": "http://nodeX:5000"}
    '''
    data = request.get_json()
    peer_url = data.get('peer_url')

    if not peer_url:
        return jsonify({"error": "peer_url required"}), 400
    
    with registry_lock:
        peer_registry.add(peer_url)

    print(f"Registered peer: {peer_url}")

    return jsonify ({
        "status": "registered",
        "total_peers": len(peer_registry)
    }), 200

@app.route('/peers', methods = ['GET'])
def get_peers():
    '''Return list of all registered peers'''
    with registry_lock:
        peers = list(peer_registry)
    
    return jsonify({"peers": peers})

if __name__ == '__main__':
    print("Starting bootstrap node on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)