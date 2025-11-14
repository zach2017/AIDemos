# Docker-in-Docker image with Docker Compose and testing tools
FROM docker:24-dind

# Install necessary packages
RUN apk add --no-cache \
    bash \
    curl \
    git \
    nodejs \
    npm \
    python3 \
    py3-pip \
    docker-compose \
    openjdk21-jre \
    maven

# Install Playwright and its dependencies
RUN npm install -g playwright@latest && \
    npx playwright install chromium && \
    npx playwright install-deps chromium

# Create working directory
WORKDIR /app

# Copy all configuration files
COPY docker-compose.yml ./
COPY spring-app/ ./spring-app/
COPY playwright-tests/ ./playwright-tests/
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x scripts/*.sh

# Entry point script
ENTRYPOINT ["/scripts/entrypoint.sh"]