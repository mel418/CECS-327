# P2P Network System

## Project Overview
A peer-to-peer distributed system with 50+ nodes using Docker.

## Prerequisites
- Docker & Docker Compose
- Python 3.9+
- PyYAML (for compose generation): `pip install pyyaml`

## Setup & Installation

1. Clone/extract the project
2. Generate large-scale compose file:
```bash
   python generate_compose.py
```

## Running the System

### Small scale (3-5 nodes):
```bash
docker-compose up -d
```

### Large scale (50-100 nodes):
```bash
docker-compose -f docker-compose-large.yml up -d
```

## Testing
```bash
# Run automated tests
python test_network.py

# Manual testing
curl http://localhost:5001/peers
curl -X POST http://localhost:5001/broadcast \
  -H "Content-Type: application/json" \
  -d '{"msg": "Hello P2P network!"}'
```

## Viewing Logs
```bash
docker-compose logs -f node1
docker logs node1
```

## Cleanup
```bash
docker-compose down
# or for large scale
docker-compose -f docker-compose-large.yml down
```

## Architecture
- Bootstrap node: Central registry for initial peer discovery
- Peer nodes: Self-discover and communicate directly
- All communication via REST API (Flask)