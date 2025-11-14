#!/bin/bash
set -e

echo "Starting Docker daemon..."
dockerd-entrypoint.sh &

# Wait for Docker daemon to be ready
echo "Waiting for Docker daemon to start..."
until docker info >/dev/null 2>&1; do
    sleep 1
done
echo "Docker daemon is ready"

# Initialize Keycloak realm and users
echo "Setting up Keycloak configuration..."
/scripts/setup-keycloak.sh &

# Initialize AWS resources
echo "Setting up AWS resources..."
/scripts/init-aws.sh

# Start all services with docker-compose
echo "Starting services with docker-compose..."
docker-compose up -d

# Wait for all services to be healthy
echo "Waiting for services to be ready..."
/scripts/wait-for-services.sh

# Run Playwright tests
echo "Running Playwright tests..."
cd /app/playwright-tests
npm install
npm test

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed"
    docker-compose logs
fi

# Keep container running for debugging if needed
tail -f /dev/null
