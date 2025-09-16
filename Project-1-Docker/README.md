# Docker Project - CECS 327

## Prerequisites
- Docker Desktop installed and running

## File Structure
```
project/
├── app.py                  # Simple Python application
├── Dockerfile              # Dockerfile for Python app
├── index.html             # Custom HTML page for Nginx
├── server.py              # TCP/UDP server application
├── Dockerfile.server      # Dockerfile for server
├── client.py              # Client application
├── Dockerfile.client      # Dockerfile for client
├── docker-compose.yml     # Multi-container setup
└── README.md              # This file
```

## How to Compile and Test

### Step 1: Verify Docker Installation
```bash
docker --version
docker run hello-world
```

### Step 2: Test Alpine Container
```bash
docker run -it alpine:latest sh
# Type 'exit' to leave
```

### Step 3: Build and Run Custom Python App
```bash
docker build -t my-python-app .
docker run my-python-app
```
**Expected Output:** `Hello, Docker! This is my first containerized app.`

### Step 4: Deploy Nginx Web Server
```bash
# Basic Nginx
docker run -d -p 8080:80 nginx:latest
```
Visit: http://localhost:8080

**With Custom HTML:**
```bash
docker run -d -p 8080:80 -v "${PWD}/index.html:/usr/share/nginx/html/index.html" nginx:latest
```

### Step 5: Multi-Container Setup
```bash
# Build and run all containers
docker-compose up --build

# View logs
docker-compose logs

# Stop all containers
docker-compose down
```

## Expected Outputs

**Python App:** `Hello, Docker! This is my first containerized app.`

**Nginx:** Browser shows welcome page at localhost:8080

**Multi-Container:** Server and client communication visible in logs

## Troubleshooting
- **Docker not running:** Start Docker Desktop
- **Port in use:** Change port mapping (e.g., `-p 8081:80`)
- **Clean up:** `docker rm -f $(docker ps -aq)`