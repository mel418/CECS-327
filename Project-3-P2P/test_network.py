import requests
import time

def test_p2p_network(num_nodes=10):
    '''Test the P2P network functionality'''

    print("Testing P2P Network...")

    # check bootstap
    print("\n1. Checking bootstrap node...")
    response = requests.get('http://localhost:5000/peers')
    peers = response.json()['peers']
    print(f"    Bootstrap knows about {len(peers)} peers")

    # check individual nodes
    print("\n2. Checking individaul nodes...")
    for i in range(1, min(num_nodes, 5) + 1):
        try:
            response = requests.get(f'http://localhost:{5000+i}/peers')
            data = response.json()
            print(f"    Node{i}: {len(data['peers'])} peers known")
        except Exception as e:
            print(f"    Node{i}: Error - {e}")
    
    # test messaging
    print("\n3. Testing message broadcast...")
    try:
        response = requests.post(
            'http://localhost:5001/broadcast',
            json={'msg': 'Test broadcast message'},
            timeout=10
        )
        results = response.json()
        print(f"    Broadcast sent to {results['total_peers']} peers")
    except Exception as e:
        print(f"    Broadcast failed: {e}")

if __name__ == '__main__':
    # wait for nodes to start
    print("Waiting for network to initialize...")
    time.sleep(10)

    test_p2p_network(50)