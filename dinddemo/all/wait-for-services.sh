#!/bin/bash

echo "Waiting for all services to be ready..."

# Function to check if a service is healthy
check_service() {
    local service=$1
    local url=$2
    local max_attempts=60
    local attempt=0
    
    echo "Checking $service..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $service is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        echo "Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 5
    done
    
    echo "❌ $service failed to become ready"
    return 1
}

# Check PostgreSQL (through Spring app's database connection)
check_service "PostgreSQL" "http://localhost:8080/actuator/health" || true

# Check Keycloak
check_service "Keycloak" "http://localhost:8180/health/ready"

# Check LocalStack
check_service "LocalStack" "http://localhost:4566/_localstack/health"

# Wait a bit more for Spring app to fully initialize
echo "Waiting for Spring application to fully initialize..."
sleep 10

# Check Spring App
check_service "Spring Application" "http://localhost:8080/actuator/health"

echo "All services are ready!"

# Verify docker-compose status
echo "Docker Compose service status:"
docker-compose ps

# Show logs for debugging
echo "Recent logs from services:"
docker-compose logs --tail=20
