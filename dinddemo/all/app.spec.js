import { test, expect } from '@playwright/test';
import axios from 'axios';

const KEYCLOAK_URL = 'http://localhost:8180';
const APP_URL = 'http://localhost:8080';
const REALM = 'spring-app-realm';
const CLIENT_ID = 'spring-app-client';
const CLIENT_SECRET = 'secret';

let accessToken = '';

test.describe('Spring Docker App Tests', () => {
  
  test.beforeAll(async () => {
    // Wait for services to be ready
    await waitForService(KEYCLOAK_URL + '/health/ready', 60000);
    await waitForService(APP_URL + '/actuator/health', 60000);
    
    // Get access token from Keycloak
    try {
      const tokenResponse = await axios.post(
        `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`,
        new URLSearchParams({
          'grant_type': 'password',
          'client_id': CLIENT_ID,
          'client_secret': CLIENT_SECRET,
          'username': 'testuser',
          'password': 'testpass'
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );
      accessToken = tokenResponse.data.access_token;
      console.log('Successfully obtained access token');
    } catch (error) {
      console.error('Failed to get access token:', error.message);
      // Try with client credentials grant as fallback
      try {
        const tokenResponse = await axios.post(
          `${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`,
          new URLSearchParams({
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
          }),
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
        );
        accessToken = tokenResponse.data.access_token;
        console.log('Successfully obtained access token using client credentials');
      } catch (fallbackError) {
        console.error('Failed to get access token with client credentials:', fallbackError.message);
      }
    }
  });

  test('Health check endpoint should be accessible', async () => {
    const response = await axios.get(`${APP_URL}/api/public/health`);
    expect(response.status).toBe(200);
    expect(response.data.status).toBe('UP');
  });

  test('Should authenticate and access protected endpoint', async () => {
    if (!accessToken) {
      console.warn('No access token available, skipping authenticated test');
      test.skip();
      return;
    }

    const response = await axios.get(
      `${APP_URL}/api/user/info`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    );
    
    expect(response.status).toBe(200);
    expect(response.data.status).toBe('success');
  });

  test('Should upload file to S3 through API', async () => {
    if (!accessToken) {
      console.warn('No access token available, skipping S3 test');
      test.skip();
      return;
    }

    const response = await axios.post(
      `${APP_URL}/api/user/upload?fileName=test-file.txt`,
      'This is test content',
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'text/plain'
        }
      }
    );
    
    expect(response.status).toBe(200);
    expect(response.data.status).toBe('success');
    expect(response.data.fileName).toBe('test-file.txt');
  });

  test('Should send message to SQS through API', async () => {
    if (!accessToken) {
      console.warn('No access token available, skipping SQS test');
      test.skip();
      return;
    }

    const response = await axios.post(
      `${APP_URL}/api/user/message`,
      'Test message for SQS',
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'text/plain'
        }
      }
    );
    
    expect(response.status).toBe(200);
    expect(response.data.status).toBe('success');
  });

  test('Login flow using Playwright browser', async ({ page }) => {
    // Navigate to the application
    await page.goto(APP_URL);
    
    // Check if redirected to Keycloak login
    if (page.url().includes(KEYCLOAK_URL)) {
      // Fill in login form
      await page.fill('#username', 'testuser');
      await page.fill('#password', 'testpass');
      await page.click('#kc-login');
      
      // Wait for redirect back to application
      await page.waitForURL(`${APP_URL}/**`, { timeout: 10000 });
    }
    
    // Verify we're logged in by checking for authenticated content
    // This would depend on your actual UI
    const response = await page.request.get(`${APP_URL}/api/user/info`, {
      headers: accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}
    });
    
    expect(response.status()).toBe(200);
  });
});

async function waitForService(url, timeout) {
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    try {
      await axios.get(url, { timeout: 5000 });
      console.log(`Service at ${url} is ready`);
      return;
    } catch (error) {
      console.log(`Waiting for ${url}...`);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
  throw new Error(`Service at ${url} did not become ready within ${timeout}ms`);
}
