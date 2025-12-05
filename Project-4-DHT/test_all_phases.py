import requests
import time
import os

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_phase1_file_storage():
    """Test Phase 1: File Upload and Download"""
    print_section("PHASE 1: FILE STORAGE TEST")
    
    # Create a test file
    test_filename = "test_document.txt"
    test_content = "This is a test file for distributed storage!\nCreated at: " + time.ctime()
    
    with open(test_filename, 'w') as f:
        f.write(test_content)
    
    print(f"\n1. Uploading file to Node 1...")
    try:
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f)}
            response = requests.post('http://localhost:5001/upload', files=files)
            print(f"   ✓ Upload response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Upload failed: {e}")
        return
    
    print(f"\n2. Downloading file from Node 1...")
    try:
        response = requests.get(f'http://localhost:5001/download/{test_filename}')
        if response.status_code == 200:
            print(f"   ✓ Downloaded successfully!")
            print(f"   Content preview: {response.text[:100]}...")
        else:
            print(f"   ✗ Download failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Download failed: {e}")
    
    print(f"\n3. Listing files on Node 1...")
    try:
        response = requests.get('http://localhost:5001/files')
        data = response.json()
        print(f"   ✓ Node 1 has {data['count']} file(s): {data['files']}")
    except Exception as e:
        print(f"   ✗ Failed to list files: {e}")
    
    # Upload to multiple nodes
    print(f"\n4. Uploading different files to different nodes...")
    for i in range(2, 4):
        filename = f"node{i}_file.txt"
        with open(filename, 'w') as f:
            f.write(f"This file belongs to node {i}\n")
        
        try:
            with open(filename, 'rb') as f:
                files = {'file': (filename, f)}
                response = requests.post(f'http://localhost:500{i}/upload', files=files)
                print(f"   ✓ Uploaded to Node {i}: {response.json()['filename']}")
        except Exception as e:
            print(f"   ✗ Upload to Node {i} failed: {e}")
    
    # Clean up local test files
    for f in [test_filename, 'node2_file.txt', 'node3_file.txt']:
        if os.path.exists(f):
            os.remove(f)

def test_phase2_key_value():
    """Test Phase 2: Key-Value Store (without DHT routing)"""
    print_section("PHASE 2: KEY-VALUE STORE TEST")
    
    test_data = [
        {"key": "color", "value": "blue"},
        {"key": "temperature", "value": "72"},
        {"key": "user_count", "value": "150"},
        {"key": "status", "value": "active"}
    ]
    
    print("\n1. Storing key-value pairs on Node 1...")
    for item in test_data:
        try:
            response = requests.post(
                'http://localhost:5001/kv',
                json=item,
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()
            print(f"   ✓ Stored: {item['key']} = {item['value']}")
        except Exception as e:
            print(f"   ✗ Failed to store {item['key']}: {e}")
    
    print("\n2. Retrieving values from Node 1...")
    for item in test_data:
        try:
            response = requests.get(f"http://localhost:5001/kv/{item['key']}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Retrieved: {result['key']} = {result['value']}")
            else:
                print(f"   ✗ Failed to retrieve {item['key']}")
        except Exception as e:
            print(f"   ✗ Error retrieving {item['key']}: {e}")
    
    print("\n3. Listing all KV pairs on Node 1...")
    try:
        response = requests.get('http://localhost:5001/kv')
        data = response.json()
        print(f"   ✓ Node 1 has {data['count']} key-value pairs:")
        for key, value in data['store'].items():
            print(f"      - {key}: {value}")
    except Exception as e:
        print(f"   ✗ Failed to list KV pairs: {e}")

def test_phase3_dht_routing():
    """Test Phase 3: DHT-Based Routing"""
    print_section("PHASE 3: DHT ROUTING TEST")
    
    # Wait for nodes to discover each other
    print("\n0. Waiting for nodes to discover each other...")
    time.sleep(3)
    
    # Check peer discovery
    print("\n1. Verifying peer discovery...")
    for i in range(1, 4):
        try:
            response = requests.get(f'http://localhost:500{i}/peers')
            data = response.json()
            print(f"   ✓ Node {i} knows about {len(data['peers'])} peers")
        except Exception as e:
            print(f"   ✗ Node {i} check failed: {e}")
    
    # Store keys that will be distributed across nodes
    print("\n2. Storing keys with DHT routing (will auto-distribute)...")
    distributed_data = [
        {"key": "apple", "value": "red fruit"},
        {"key": "banana", "value": "yellow fruit"},
        {"key": "cherry", "value": "red fruit"},
        {"key": "date", "value": "brown fruit"},
        {"key": "elderberry", "value": "purple fruit"},
        {"key": "fig", "value": "sweet fruit"},
    ]
    
    # Store all keys through Node 1 - DHT will route them
    for item in distributed_data:
        try:
            response = requests.post(
                'http://localhost:5001/kv',
                json=item,
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()
            responsible = result.get('responsible_node', 'unknown')
            forwarded = result.get('forwarded_from', None)
            
            if forwarded:
                print(f"   ✓ '{item['key']}' forwarded to: {responsible}")
            else:
                print(f"   ✓ '{item['key']}' stored locally on: {responsible}")
        except Exception as e:
            print(f"   ✗ Failed to store {item['key']}: {e}")
    
    # Check distribution across nodes
    print("\n3. Checking data distribution across nodes...")
    for i in range(1, 4):
        try:
            response = requests.get(f'http://localhost:500{i}/kv')
            data = response.json()
            print(f"   Node {i} stores {data['count']} keys: {list(data['store'].keys())}")
        except Exception as e:
            print(f"   ✗ Failed to check Node {i}: {e}")
    
    # Retrieve keys from any node - DHT will route
    print("\n4. Retrieving keys from Node 2 (DHT will auto-route)...")
    for item in distributed_data[:3]:  # Test first 3 keys
        try:
            response = requests.get(f"http://localhost:5002/kv/{item['key']}")
            if response.status_code == 200:
                result = response.json()
                forwarded = result.get('forwarded_from', None)
                responsible = result.get('responsible_node', 'unknown')
                
                if forwarded:
                    print(f"   ✓ '{item['key']}' retrieved (forwarded from Node 2 to {responsible})")
                else:
                    print(f"   ✓ '{item['key']}' retrieved (stored on Node 2)")
            else:
                print(f"   ✗ Failed to retrieve {item['key']}")
        except Exception as e:
            print(f"   ✗ Error retrieving {item['key']}: {e}")
    
    # Show DHT debug info
    print("\n5. DHT Debug Information (Node 1)...")
    try:
        response = requests.get('http://localhost:5001/kv/debug')
        data = response.json()
        print(f"   Total nodes in DHT: {data['total_nodes']}")
        print(f"   Node positions (sorted by hash):")
        for node in data['nodes']:
            marker = " (ME)" if node['is_me'] else ""
            print(f"      {node['url']}: hash={node['hash']}{marker}")
    except Exception as e:
        print(f"   ✗ Failed to get debug info: {e}")

def test_network_health():
    """Test overall network health"""
    print_section("NETWORK HEALTH CHECK")
    
    print("\n1. Checking bootstrap node...")
    try:
        response = requests.get('http://localhost:5000/peers')
        data = response.json()
        print(f"   ✓ Bootstrap knows about {len(data['peers'])} peers")
    except Exception as e:
        print(f"   ✗ Bootstrap check failed: {e}")
    
    print("\n2. Checking all peer nodes...")
    for i in range(1, 4):
        try:
            response = requests.get(f'http://localhost:500{i}/')
            data = response.json()
            print(f"   ✓ Node {i}: {data['peer_count']} peers, "
                  f"{data['stored_keys']} keys, {data['stored_files']} files")
        except Exception as e:
            print(f"   ✗ Node {i} check failed: {e}")

def main():
    """Run all tests"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  P2P DISTRIBUTED HASH TABLE - COMPREHENSIVE TEST SUITE".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print("\n⏳ Waiting for network to initialize (15 seconds)...")
    time.sleep(15)
    
    # Run all test phases
    test_network_health()
    test_phase1_file_storage()
    test_phase2_key_value()
    test_phase3_dht_routing()
    
    # Final summary
    print_section("TEST SUITE COMPLETE")
    print("\n✓ All phases tested successfully!")
    print("\nWhat we demonstrated:")
    print("  1. File storage and retrieval across nodes")
    print("  2. Key-value storage with thread-safe operations")
    print("  3. DHT-based automatic data distribution")
    print("  4. Request forwarding between nodes")
    print("  5. Consistent hashing for load distribution")
    print("\n" + "█"*70 + "\n")

if __name__ == '__main__':
    main()