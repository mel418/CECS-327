# Docker Project - CECS 327

## How to Compile and Test

### Step 1: Verify Docker
```bash
docker --version
docker run hello-world
```

### Step 2: Python App
```bash
docker build -t my-python-app .
docker run my-python-app
```

### Step 3: Nginx Server
```bash
# Basic Nginx
docker run -d -p 8080:80 nginx:latest

# With custom HTML
docker run -d -p 8080:80 -v "${PWD}/index.html:/usr/share/nginx/html/index.html" nginx:latest
```
Visit: http://localhost:8080

### Step 4: Multi-Container
```bash
docker-compose up --build
docker-compose down
```

## Useful Commands
```bash
# View running containers
docker ps

# Stop and remove containers
docker stop <container_name>
docker rm <container_name>

# Clean up all containers
docker rm -f $(docker ps -aq)
```

## Expected Outputs
- Python App: "Hello, Docker! This is my first containerized app."
- Nginx: Welcome page at localhost:8080
- Multi-Container: Server-client communication in logs