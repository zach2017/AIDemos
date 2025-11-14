#!/bin/bash

KEYCLOAK_URL="http://localhost:8180"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
REALM_NAME="spring-app-realm"
CLIENT_ID="spring-app-client"
CLIENT_SECRET="secret"

echo "Waiting for Keycloak to be ready..."
until curl -s "${KEYCLOAK_URL}/health/ready" | grep -q "UP"; do
    sleep 5
done

echo "Keycloak is ready. Setting up realm and client..."

# Get admin token
TOKEN=$(curl -s -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${ADMIN_USER}" \
    -d "password=${ADMIN_PASSWORD}" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "Failed to get admin token"
    exit 1
fi

# Create realm
curl -s -X POST "${KEYCLOAK_URL}/admin/realms" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "realm": "'${REALM_NAME}'",
        "enabled": true,
        "sslRequired": "none",
        "registrationAllowed": false,
        "loginWithEmailAllowed": true,
        "duplicateEmailsAllowed": false,
        "resetPasswordAllowed": false,
        "editUsernameAllowed": false,
        "bruteForceProtected": true
    }'

echo "Realm '${REALM_NAME}' created"

# Create client
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "'${CLIENT_ID}'",
        "enabled": true,
        "clientAuthenticatorType": "client-secret",
        "secret": "'${CLIENT_SECRET}'",
        "redirectUris": ["http://localhost:8080/*"],
        "webOrigins": ["http://localhost:8080"],
        "publicClient": false,
        "serviceAccountsEnabled": true,
        "directAccessGrantsEnabled": true,
        "authorizationServicesEnabled": false,
        "protocol": "openid-connect",
        "bearerOnly": false,
        "standardFlowEnabled": true
    }'

echo "Client '${CLIENT_ID}' created"

# Create test user
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser",
        "enabled": true,
        "emailVerified": true,
        "firstName": "Test",
        "lastName": "User",
        "email": "testuser@example.com",
        "credentials": [{
            "type": "password",
            "value": "testpass",
            "temporary": false
        }]
    }'

echo "Test user 'testuser' created"

# Get the client's ID (not clientId)
CLIENT_UUID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients?clientId=${CLIENT_ID}" \
    -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id')

# Get service account user
SERVICE_ACCOUNT_USER=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients/${CLIENT_UUID}/service-account-user" \
    -H "Authorization: Bearer ${TOKEN}" | jq -r '.id')

echo "Keycloak setup completed successfully"
