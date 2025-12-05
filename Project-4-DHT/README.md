# P2P Network System

## Project Overview
A peer-to-peer distributed system with 50+ nodes using Docker.

## Prerequisites
- Docker & Docker Compose
- Python 3.9+
- PyYAML (for compose generation): `pip install pyyaml`

## Setup & Installation

1. Clone/extract the project
2. Install PyYAML:
```powershell
   pip install pyyaml
```
3. Generate large-scale compose file:
```powershell
   python generate_compose.py
```

## Running the System

### Small scale (3 nodes + bootstrap):
```powershell
docker-compose up -d
```

### Large scale (50 nodes + bootstrap):
```powershell
docker-compose -f docker-compose-large.yml up -d
```

## Testing

### Check Bootstrap Node
```powershell
curl.exe http://localhost:5000/peers
```

### Check Individual Node Peers
```powershell
curl.exe http://localhost:5001/peers
curl.exe http://localhost:5002/peers
curl.exe http://localhost:5003/peers
```

### Test Message Broadcasting
```powershell
# PowerShell - use escaped quotes
curl.exe -X POST http://localhost:5001/broadcast -H "Content-Type: application/json" -d '{\"msg\": \"Hello P2P network!\"}'
```

### Run Automated Tests
```powershell
python test_network.py
```

## Viewing Logs

### Small Network
```powershell
docker-compose logs node1
docker-compose logs node2
docker-compose logs -f node3
```

### Large Network
```powershell
docker-compose -f docker-compose-large.yml logs node1
docker-compose -f docker-compose-large.yml logs node25
docker-compose -f docker-compose-large.yml logs -f node50
```

## Cleanup

### Small Network
```powershell
docker-compose down
```

### Large Network
```powershell
docker-compose -f docker-compose-large.yml down
```

### Remove All Containers and Networks
```powershell
docker-compose down -v
docker system prune -f
```

## Architecture
- **Bootstrap node**: Central registry for initial peer discovery
- **Peer nodes**: Auto-discover and communicate directly via P2P
- **Communication**: RESTful API using Flask
- **Discovery**: Nodes automatically discover peers every 30 seconds
- **Thread-safe**: Uses locks for concurrent peer management

## API Endpoints

### Node Endpoints
- `GET /` - Health check and node status
- `GET /peers` - Get list of known peers
- `POST /message` - Receive a message from another peer
```json
  {"sender": "node_id", "msg": "Hello!"}
```
- `POST /broadcast` - Broadcast message to all known peers
```json
  {"msg": "Hello everyone!"}
```

### Bootstrap Endpoints
- `GET /` - Bootstrap node status
- `POST /register` - Register a new peer
```json
  {"peer_url": "http://nodeX:5000"}
```
- `GET /peers` - Get all registered peers

