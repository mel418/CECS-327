# P2P Distributed Hash Table Network


### Prerequisites
- Docker Desktop (running)
- Python 3.9+

### Build
```powershell
docker-compose build
```

### Run
```powershell
docker-compose up -d
```
Wait 15 seconds for nodes to initialize.

### Test

Phase 1 - File Storage:
```powershell
echo "Hello DHT!" > test.txt
curl.exe -F "file=@test.txt" http://localhost:5001/upload
curl.exe http://localhost:5001/download/test.txt
```

Phase 2 - Key-Value Store:
```powershell
curl.exe -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{\"key\": \"color\", \"value\": \"blue\"}'
curl.exe http://localhost:5001/kv/color
```

Phase 3 - DHT Routing:
```powershell
curl.exe -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{\"key\": \"apple\", \"value\": \"red\"}'
curl.exe -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{\"key\": \"banana\", \"value\": \"yellow\"}'
curl.exe http://localhost:5001/kv
curl.exe http://localhost:5002/kv
curl.exe http://localhost:5003/kv
```

### Stop
```powershell
docker-compose down
```