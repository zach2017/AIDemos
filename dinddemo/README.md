# Docker-in-Docker Spring Boot Testing Environment

This project provides a complete Docker-in-Docker (DinD) environment that runs a full-stack application with automated testing using Playwright.

## Architecture Overview

The setup includes:
- **Spring Boot Application** (Java 21) - REST API with OAuth2 security
- **Keycloak** - OAuth2/OpenID Connect authentication server
- **PostgreSQL** - Database backend
- **LocalStack** - AWS services simulation (S3 and SQS)
- **Playwright** - End-to-end testing framework

## Services and Ports

- Spring Boot App: http://localhost:8080
- Keycloak Admin: http://localhost:8180 (admin/admin)
- LocalStack: http://localhost:4566
- PostgreSQL: localhost:5432 (dbuser/dbpass)

## Prerequisites

- Docker installed on your host machine
- At least 8GB of available RAM
- Ports 8080, 8180, 4566, and 5432 available

## Quick Start

1. Make the build script executable:
```bash
chmod +x build-and-run.sh
chmod +x scripts/*.sh
```

2. Build and run the entire environment:
```bash
./build-and-run.sh
```

This will:
1. Build the Docker-in-Docker image
2. Start all services using docker-compose
3. Initialize Keycloak with realm and test user
4. Create AWS resources (S3 bucket and SQS queue)
5. Run Playwright tests automatically

## Manual Testing

### Test Credentials
- **Keycloak Admin**: admin/admin
- **Test User**: testuser/testpass
- **Client ID**: spring-app-client
- **Client Secret**: secret

### API Endpoints

#### Public Endpoints (No Auth Required)
- `GET /api/public/health` - Health check

#### Protected Endpoints (OAuth2 Token Required)
- `GET /api/user/info` - Get user information
- `POST /api/user/upload?fileName={name}` - Upload to S3
- `POST /api/user/message` - Send message to SQS

### Getting an Access Token

```bash
curl -X POST http://localhost:8180/realms/spring-app-realm/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=spring-app-client" \
  -d "client_secret=secret" \
  -d "username=testuser" \
  -d "password=testpass"
```

### Using the Access Token

```bash
TOKEN="your_access_token_here"

# Call protected endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/user/info

# Upload to S3
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/plain" \
  -d "File content here" \
  "http://localhost:8080/api/user/upload?fileName=test.txt"

# Send SQS message
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/plain" \
  -d "Test message" \
  http://localhost:8080/api/user/message
```

## Project Structure

```
.
├── Dockerfile                 # Main DinD container definition
├── docker-compose.yml         # Service orchestration
├── build-and-run.sh          # Build and run script
├── spring-app/               # Spring Boot application
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/
│       └── main/
│           ├── java/         # Java source code
│           └── resources/    # Application configuration
├── playwright-tests/         # E2E tests
│   ├── package.json
│   ├── playwright.config.js
│   └── tests/
│       └── app.spec.js      # Test specifications
└── scripts/                  # Setup and utility scripts
    ├── entrypoint.sh
    ├── init-aws.sh
    ├── setup-keycloak.sh
    └── wait-for-services.sh
```

## Troubleshooting

### Services Not Starting
- Check Docker logs: `docker logs spring-test-container`
- Verify port availability: `netstat -tulpn | grep -E '8080|8180|4566|5432'`

### Keycloak Issues
- Access Keycloak admin console: http://localhost:8180
- Default admin credentials: admin/admin
- Check realm configuration in the admin console

### LocalStack Issues
- Verify LocalStack health: `curl http://localhost:4566/_localstack/health`
- Check S3 buckets: `aws --endpoint-url=http://localhost:4566 s3 ls`
- Check SQS queues: `aws --endpoint-url=http://localhost:4566 sqs list-queues`

### Test Failures
- Check Playwright report: Look for `playwright-report` folder
- View container logs: `docker exec spring-test-container docker-compose logs`
- Run tests manually: `docker exec spring-test-container npm test --prefix /app/playwright-tests`

## Customization

### Adding More Tests
Edit `/playwright-tests/tests/app.spec.js` to add more test cases.

### Modifying Spring Application
Update files in `/spring-app/src/` and rebuild the Docker image.

### Adding AWS Services
1. Update LocalStack `SERVICES` environment variable in `docker-compose.yml`
2. Add initialization commands in `/scripts/init-aws.sh`
3. Update Spring application to use new services

## Cleanup

To stop and remove all containers:
```bash
docker stop spring-test-container
docker system prune -f
```

## Security Notes

This setup is for development/testing only. For production:
- Use proper SSL/TLS certificates
- Change all default passwords
- Configure proper network isolation
- Use production-grade Keycloak configuration
- Implement proper secret management

## License

This is a sample project for demonstration purposes.