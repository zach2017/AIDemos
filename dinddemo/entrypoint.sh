#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Docker-in-Docker Testing Environment${NC}"
echo "================================================"

# Build the main Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t spring-dind-test .

# Run the container with necessary privileges for Docker-in-Docker
echo -e "${YELLOW}Starting Docker container...${NC}"
docker run -it \
    --privileged \
    --name spring-test-container \
    --rm \
    -p 8080:8080 \
    -p 8180:8180 \
    -p 4566:4566 \
    -p 5432:5432 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    spring-dind-test

echo -e "${GREEN}Container stopped${NC}"