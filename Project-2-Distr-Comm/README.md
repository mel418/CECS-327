# Distributed Communication Project

This project demonstrates Anycast (TCP) and Multicast (UDP) communication patterns using Docker containers.

## Prerequisites
- Docker
- Docker Compose

## Test Anycast (in anycast folder):
```bash
cd anycast

# Build and start
docker-compose up -d

# Check all containers are running
docker-compose ps

# Test client multiple times
docker exec anycast_client python client.py
docker exec anycast_client python client.py
docker exec anycast_client python client.py
docker exec anycast_client python client.py
docker exec anycast_client python client.py

# View server logs
docker-compose logs -f

# Capture traffic on one server
docker exec anycast_server1 tcpdump -i eth0 tcp port 5000 -n

# When done
docker-compose down
```

## Test Multicast (in multicast folder):
```bash
cd multicast

# Build and start
docker-compose -f docker-compose-multicast.yml up -d

# Watch logs in real-time
docker-compose -f docker-compose-multicast.yml logs -f

# In another terminal, capture traffic
docker exec multicast_receiver1 tcpdump -i eth0 udp port 5007 -n -v

# Let it run for about 1 minute to see the behavior

# When done
docker-compose -f docker-compose-multicast.yml down
```