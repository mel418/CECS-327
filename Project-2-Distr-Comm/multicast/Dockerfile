FROM python:3.9-slim

# install tcpdump for network monitoring
RUN apt-get  update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*

# set working dir
WORKDIR /app

COPY server.py client.py ./

# Default command (will be overridden in docker-compose)
CMD ["python", "server.py"]