# Docker Project - CECS 327

## Group Information
- **Group Members:**
  - [Name 1] - [Student ID]
  - [Name 2] - [Student ID]
  - [Name 3] - [Student ID]

## Project Overview
This project demonstrates Docker containerization through:
1. Running basic containers
2. Creating custom Docker images
3. Deploying web servers
4. Multi-container communication using Docker Compose

## Prerequisites
- Docker Desktop installed and running
- Basic command line knowledge
- Python 3.x (for development, not required for running containers)

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
# Inside container: explore with ls, echo, etc.
# Type 'exit' to leave
```

### Step 3: Build and Run Custom Python App
```bash
# Build the image
docker build -t my-python-app .

# Run the container
docker run my-python-app
```
**Expected Output:** `Hello, Docker! This is my first containerized app.`

### Step 4: Deploy Nginx Web Server

**Basic Nginx:**
```bash
docker pull nginx:latest
docker run -d -p 8080:80 --name my-nginx nginx:latest
```
Visit: http://localhost:8080

**With Custom HTML:**
```bash
# Stop previous container
docker stop my-nginx
docker rm my-nginx

# Run with custom page (PowerShell)
docker run -d -p 8080:80 -v "${PWD}/index.html:/usr/share/nginx/html/index.html" nginx:latest
```
Visit: http://localhost:8080 to see custom page

### Step 5: Multi-Container Setup
```bash
# Build and run all containers
docker-compose up --build

# To run in background
docker-compose up -d --build

# View logs
docker-compose logs

# Stop all containers
docker-compose down
```

## Expected Outputs

### Python App Container
```
Hello, Docker! This is my first containerized app.
```

### Nginx Server
- Browser shows "Welcome to nginx!" page
- With custom HTML: Shows your custom page

### Multi-Container Communication
```
Server logs should show:
- TCP Server listening on port 8001...
- UDP Server listening on port 8002...
- TCP connection from <client_ip>
- TCP received from <client_ip>: Hello from TCP client 1, message 1
- UDP received from <client_ip>: Hello from UDP client 1, message 1

Client logs should show:
- TCP Client 1 received: Server received: Hello from TCP client 1, message 1
- UDP Client 1 received: Server received: Hello from UDP client 1, message 1
```

## Troubleshooting

### Common Issues
1. **Docker not running:** Start Docker Desktop
2. **Port already in use:** Change port mapping (e.g., `-p 8081:80`)
3. **Permission denied:** Run Docker Desktop as administrator
4. **Container won't start:** Check logs with `docker logs <container_name>`

### Useful Commands
```bash
# List running containers
docker ps

# View container logs
docker logs <container_name>

# Enter running container
docker exec -it <container_name> sh

# Clean up all containers
docker rm -f $(docker ps -aq)

# Clean up system
docker system prune
```

## Testing Checklist
- [ ] Docker installation verified
- [ ] Alpine container runs successfully
- [ ] Python app builds and runs
- [ ] Nginx serves default page on localhost:8080
- [ ] Nginx serves custom HTML page
- [ ] Multi-container setup builds successfully
- [ ] Server-client communication works (check logs)
- [ ] All containers can be stopped and started

## Video Demonstration
[Insert YouTube link here showing code execution and outputs]

## Notes
- Ensure Docker Desktop is running before executing any commands
- All containers should be built and tested on the same machine
- Screenshots and detailed logs are included in the project report