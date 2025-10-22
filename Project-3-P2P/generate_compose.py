import yaml

def generate_compose(num_nodes):
    config = {
        'version': '3.8',
        'services': {},
        'networks': {
            'p2p-network': {'driver': 'bridge'}
        }
    }

    # bootstrap node
    config['services']['bootstrap'] = {
        'build': {
            'context': '.',
            'dockerfile': 'bootstrap.Dockerfile'
        },
        'container_name': 'bootstrap',  # FIXED: was 'container-name'
        'ports': ['5000:5000'],
        'networks': ['p2p-network']
    }

    # generate peer nodes
    for i in range(1, num_nodes + 1):
        node_name = f'node{i}'
        config['services'][node_name] = {
            'build': {
                'context': '.',
                'dockerfile': 'Dockerfile'
            },
            'container_name': node_name,
            'environment': [
                'BOOTSTRAP_URL=http://bootstrap:5000',
                f'NODE_URL=http://{node_name}:5000'
            ],
            'ports': [f'{5000+i}:5000'],
            'depends_on': ['bootstrap'],
            'networks': ['p2p-network']
        }
    
    with open('docker-compose-large.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"Generated docker-compose-large.yml with {num_nodes} nodes")

if __name__ == '__main__':
    generate_compose(50)  # change to 100 if needed