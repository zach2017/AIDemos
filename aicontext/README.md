# Java Spring OAuth2 Tutorial: Complete Guide with Keycloak

## Overview

This tutorial explains how OAuth2 authentication works in a Spring Boot application using Keycloak as the identity provider. We'll break down each component and show how a React client can integrate with this backend.

---

## Table of Contents

1. [OAuth2 Flow Overview](#oauth2-flow-overview)
2. [Security Configuration Deep Dive](#security-configuration-deep-dive)
3. [OAuth2 Callback Controller](#oauth2-callback-controller)
4. [React Client Integration](#react-client-integration)
5. [Key Concepts Summary](#key-concepts-summary)

---

## OAuth2 Flow Overview

### The Authorization Code Flow

This implementation uses the **OAuth2 Authorization Code Grant** flow, which is the most secure flow for web applications:

```
1. User → Your App: "I want to access protected resources"
2. Your App → Keycloak: "Redirect user to login"
3. User → Keycloak: "Login with credentials"
4. Keycloak → Your App: "Here's an authorization code"
5. Your App → Keycloak: "Exchange code for access token"
6. Keycloak → Your App: "Here's the access token"
7. Your App → User: "Store token in cookie, you're authenticated"
```

**Key Concepts:**
- **Authorization Code**: Temporary code received after user login (short-lived, single-use)
- **Access Token**: JWT token that proves user identity (used for API requests)
- **Redirect URI**: Where Keycloak sends the user after authentication
- **Client ID/Secret**: Credentials that identify your application to Keycloak

---

## Security Configuration Deep Dive

### File: `SecurityConfig.java`

This class sets up the entire security layer for your Spring Boot application.

### 1. Configuration Properties

```java
@Value("${keycloak.auth-server-url}")
private String keycloakUrl;

@Value("${keycloak.realm}")
private String realm;

@Value("${keycloak.client-id}")
private String clientId;

@Value("${keycloak.redirect-uri}")
private String redirectUri;
```

**What it does:**
- Injects Keycloak configuration from `application.properties` or `application.yml`
- Keeps sensitive configuration separate from code

**Key Concepts:**
- **Realm**: Logical namespace in Keycloak that groups users, roles, and clients
- **Client ID**: Unique identifier for your application
- **Redirect URI**: Must match exactly what's configured in Keycloak (security measure)

---

### 2. Security Filter Chain

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .addFilterBefore(cookieToHeaderFilter(), UsernamePasswordAuthenticationFilter.class)
        .authorizeHttpRequests(authz -> authz
            .requestMatchers("/oauth2/callback", "/error").permitAll()
            .requestMatchers("**").authenticated()
            .anyRequest().authenticated()
        )
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt()
            .and()
            .authenticationEntryPoint(keycloakAuthenticationEntryPoint())
        )
        .csrf(csrf -> csrf.disable());
    
    return http.build();
}
```

**What it does:**
- Configures which endpoints require authentication
- Sets up JWT validation for protected endpoints
- Adds custom filter to handle cookie-based authentication

**Breaking it down:**

#### a) Filter Chain Order
```java
.addFilterBefore(cookieToHeaderFilter(), UsernamePasswordAuthenticationFilter.class)
```
- Adds custom cookie filter **before** Spring's standard authentication filter
- This allows extracting JWT from cookies instead of requiring Authorization header

#### b) Authorization Rules
```java
.authorizeHttpRequests(authz -> authz
    .requestMatchers("/oauth2/callback", "/error").permitAll()
    .requestMatchers("**").authenticated()
    .anyRequest().authenticated()
)
```

**Key Concepts:**
- **permitAll()**: Public endpoints (no authentication required)
  - `/oauth2/callback`: Must be public to receive authorization code
  - `/error`: Standard error endpoint
- **authenticated()**: All other endpoints require valid JWT token

#### c) OAuth2 Resource Server
```java
.oauth2ResourceServer(oauth2 -> oauth2
    .jwt()
    .and()
    .authenticationEntryPoint(keycloakAuthenticationEntryPoint())
)
```

**What it does:**
- Configures app as an OAuth2 Resource Server (API that accepts JWT tokens)
- Validates JWT tokens automatically
- Uses custom entry point for unauthorized requests

**Key Concepts:**
- **Resource Server**: Backend API that validates and accepts access tokens
- **JWT Validation**: Spring automatically verifies token signature, expiration, issuer

#### d) CSRF Protection
```java
.csrf(csrf -> csrf.disable())
```
- Disables CSRF protection (common for stateless REST APIs)
- Since we're using JWT tokens (not session cookies), CSRF is not needed

---

### 3. Authentication Entry Point

```java
@Bean
public AuthenticationEntryPoint keycloakAuthenticationEntryPoint() {
    return (request, response, authException) -> {
        if (request.getRequestURI().startsWith("/api")) {
            String authorizationUrl = String.format(
                "%s/realms/%s/protocol/openid-connect/auth?client_id=%s&redirect_uri=%s&response_type=code&scope=openid",
                keycloakUrl, realm, clientId, redirectUri
            );
            response.sendRedirect(authorizationUrl);
        } else {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Unauthorized");
        }
    };
}
```

**What it does:**
- Handles what happens when an unauthenticated user tries to access protected resources
- For API endpoints: redirects to Keycloak login page
- For other endpoints: returns 401 Unauthorized

**The Keycloak Authorization URL:**
```
https://keycloak.example.com/realms/my-realm/protocol/openid-connect/auth
  ?client_id=my-app
  &redirect_uri=http://localhost:8080/oauth2/callback
  &response_type=code
  &scope=openid
```

**Key Concepts:**
- **response_type=code**: Requests authorization code (not token directly)
- **scope=openid**: Requests OpenID Connect authentication
- **redirect_uri**: Where Keycloak sends user after authentication

---

### 4. Cookie to Header Filter

```java
@Bean
public OncePerRequestFilter cookieToHeaderFilter() {
    return new OncePerRequestFilter() {
        @Override
        protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, 
                                      FilterChain filterChain) throws ServletException, IOException {
            
            if (request.getRequestURI().startsWith("/api")) {
                if (request.getCookies() != null) {
                    for (Cookie cookie : request.getCookies()) {
                        if ("access_token".equals(cookie.getName())) {
                            HttpServletRequest wrappedRequest = new HttpServletRequestWrapper(request) {
                                @Override
                                public String getHeader(String name) {
                                    if ("Authorization".equalsIgnoreCase(name)) {
                                        return "Bearer " + cookie.getValue();
                                    }
                                    return super.getHeader(name);
                                }
                            };
                            filterChain.doFilter(wrappedRequest, response);
                            return;
                        }
                    }
                }
            }
            
            filterChain.doFilter(request, response);
        }
    };
}
```

**What it does:**
- Extracts JWT token from `access_token` cookie
- Converts it to standard `Authorization: Bearer <token>` header
- Allows cookie-based authentication instead of manually adding headers

**Why this matters:**
- Cookies are automatically sent by browsers
- React client doesn't need to manually manage tokens
- More secure than localStorage (HttpOnly cookies can't be accessed by JavaScript)

**Key Concepts:**
- **OncePerRequestFilter**: Executes once per request (before reaching controller)
- **HttpServletRequestWrapper**: Wraps original request to modify headers
- **Bearer Token**: Standard format for JWT tokens in Authorization header

---

## OAuth2 Callback Controller

### File: `OAuth2CallbackController.java`

This controller handles the OAuth2 callback after user authenticates with Keycloak.

### 1. Callback Endpoint

```java
@GetMapping("/oauth2/callback")
public void handleCallback(
        @RequestParam("code") String code,
        @RequestParam(value = "error", required = false) String error,
        @RequestParam(value = "error_description", required = false) String errorDescription,
        HttpServletResponse response) throws Exception
```

**What it does:**
- Receives authorization code from Keycloak after successful login
- Handles potential errors from authentication process

**The callback URL looks like:**
```
http://localhost:8080/oauth2/callback?code=AUTH_CODE_HERE
```

Or if there's an error:
```
http://localhost:8080/oauth2/callback?error=access_denied&error_description=User+cancelled
```

**Key Concepts:**
- **Authorization Code**: Single-use, short-lived code to exchange for token
- **Error Handling**: Keycloak returns errors via query parameters

---

### 2. Error Checking

```java
if (error != null) {
    response.sendError(HttpServletResponse.SC_BAD_REQUEST, 
        "OAuth2 Error: " + error + " - " + errorDescription);
    return;
}
```

**What it does:**
- Checks if Keycloak returned an error (user cancelled, access denied, etc.)
- Returns appropriate error response to client

---

### 3. Token Exchange

```java
String tokenEndpoint = String.format(
    "%s/realms/%s/protocol/openid-connect/token",
    keycloakUrl, realm
);

RestTemplate restTemplate = new RestTemplate();
HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
body.add("grant_type", "authorization_code");
body.add("client_id", clientId);
body.add("client_secret", clientSecret);
body.add("code", code);
body.add("redirect_uri", redirectUri);

HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(body, headers);
ResponseEntity<Map> tokenResponse = restTemplate.postForEntity(
    tokenEndpoint, request, Map.class
);
```

**What it does:**
- Makes POST request to Keycloak's token endpoint
- Exchanges authorization code for access token
- Uses client credentials to authenticate the application

**The Token Request:**
```
POST https://keycloak.example.com/realms/my-realm/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id=my-app
&client_secret=SECRET
&code=AUTH_CODE
&redirect_uri=http://localhost:8080/oauth2/callback
```

**Key Concepts:**
- **grant_type=authorization_code**: Specifies we're exchanging a code
- **client_secret**: Proves application identity (NEVER expose in frontend)
- **redirect_uri**: Must match original request (security check)

---

### 4. Token Response

```java
String accessToken = (String) tokenResponse.getBody().get("access_token");
Integer expiresIn = (Integer) tokenResponse.getBody().get("expires_in");
```

**Keycloak returns:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "not-before-policy": 0,
  "session_state": "uuid",
  "scope": "openid email profile"
}
```

**Key Concepts:**
- **access_token**: JWT token for API authentication
- **expires_in**: Seconds until token expires (typically 3600 = 1 hour)
- **refresh_token**: Can be used to get new access token without re-login

---

### 5. Cookie Storage

```java
Cookie tokenCookie = new Cookie("access_token", accessToken);
tokenCookie.setHttpOnly(true);
tokenCookie.setSecure(false); // Set to true in production with HTTPS
tokenCookie.setPath("/");
tokenCookie.setMaxAge(expiresIn != null ? expiresIn : 3600);
response.addCookie(tokenCookie);
```

**What it does:**
- Stores access token in HttpOnly cookie
- Cookie is automatically sent with all subsequent requests

**Cookie Configuration:**
- **HttpOnly**: JavaScript cannot access (prevents XSS attacks)
- **Secure**: Only sent over HTTPS (set to true in production)
- **Path**: Cookie sent for all paths on domain
- **MaxAge**: Cookie expires when token expires

**Key Concepts:**
- **HttpOnly Cookie**: More secure than localStorage for token storage
- **XSS Protection**: Even if site has XSS vulnerability, token can't be stolen
- **Automatic Management**: Browser handles sending cookie with requests

---

### 6. Final Redirect

```java
response.sendRedirect("/api/user-info");
```

**What it does:**
- Redirects user to protected endpoint (now with valid token in cookie)
- Triggers the cookie filter which extracts token for authentication

---

## React Client Integration

### How Your React App Would Use This System

#### Step 1: Initial Login Request

When user clicks "Login" button:

```javascript
// React Component
function LoginButton() {
  const handleLogin = () => {
    // Redirect to your backend, which redirects to Keycloak
    window.location.href = 'http://localhost:8080/api/protected-resource';
  };

  return <button onClick={handleLogin}>Login with Keycloak</button>;
}
```

**What happens:**
1. User clicks button
2. Browser requests protected resource
3. Backend sees no valid token
4. Backend redirects to Keycloak login page
5. User enters credentials on Keycloak
6. Keycloak redirects back to `/oauth2/callback` with code
7. Backend exchanges code for token
8. Backend stores token in cookie
9. Backend redirects to `/api/user-info`
10. React receives user info

---

#### Step 2: Accessing Protected Resources

After authentication, all API calls work automatically:

```javascript
// React Component
import { useState, useEffect } from 'react';

function UserProfile() {
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8080/api/user-info', {
      credentials: 'include', // IMPORTANT: Sends cookies
      headers: {
        'Accept': 'application/json',
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Unauthorized');
        }
        return response.json();
      })
      .then(data => {
        setUserInfo(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Welcome, {userInfo.name}</h2>
      <p>Email: {userInfo.email}</p>
      <p>Username: {userInfo.username}</p>
    </div>
  );
}
```

**Key Points:**
- **credentials: 'include'**: Essential! Tells fetch to send cookies
- **No manual token management**: Browser handles everything
- **Automatic authentication**: Cookie filter extracts token from cookie

---

#### Step 3: Complete React Authentication Flow

```javascript
// AuthContext.js
import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/user-info', {
        credentials: 'include',
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    // Redirect to backend which initiates OAuth flow
    window.location.href = 'http://localhost:8080/api/user-info';
  };

  const logout = async () => {
    try {
      await fetch('http://localhost:8080/api/logout', {
        method: 'POST',
        credentials: 'include',
      });
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

---

#### Step 4: Protected Routes

```javascript
// ProtectedRoute.js
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// App.js
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './AuthContext';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <UserProfile />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

---

#### Step 5: Making Authenticated API Calls

```javascript
// api.js - Centralized API calls
const API_BASE_URL = 'http://localhost:8080/api';

export const apiClient = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      credentials: 'include', // Always include cookies
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Redirect to login if unauthorized
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },
};

// Usage in components
function MyComponent() {
  const [data, setData] = useState([]);

  useEffect(() => {
    apiClient.get('/users')
      .then(setData)
      .catch(console.error);
  }, []);

  return <div>{/* Render data */}</div>;
}
```

---

## Key Concepts Summary

### OAuth2 Flow
- **Authorization Code Grant**: Most secure OAuth2 flow for web apps
- **Three-legged OAuth**: User, Client App, and Authorization Server all involved
- **Code Exchange**: Authorization code is temporary and exchanged for token
- **Token Storage**: Access token stored in HttpOnly cookie for security

### Security Configuration
- **SecurityFilterChain**: Defines which endpoints require authentication
- **Resource Server**: Your backend validates JWT tokens from Keycloak
- **Custom Filter**: Extracts token from cookie and adds to Authorization header
- **Entry Point**: Handles what happens when unauthenticated user accesses protected resource

### Token Management
- **JWT (JSON Web Token)**: Self-contained token with user info and signature
- **HttpOnly Cookies**: Secure storage that JavaScript cannot access
- **Automatic Validation**: Spring validates token signature, expiration, issuer
- **Stateless Authentication**: No session storage needed on backend

### React Integration
- **credentials: 'include'**: Must be set on all fetch requests to send cookies
- **Automatic Authentication**: Browser manages cookie sending
- **No Token in Code**: Token never appears in JavaScript (security)
- **Redirect-based Login**: User redirected to Keycloak, then back to app

### Best Practices Demonstrated
- **Separation of Concerns**: Security config separate from business logic
- **Configuration Management**: External config for environment-specific values
- **Error Handling**: Proper error responses for OAuth failures
- **Cookie Security**: HttpOnly, Secure flags, appropriate expiration
- **CORS Configuration**: Needed for React (separate domain) to send cookies

---

## Security Considerations

### Production Checklist

1. **HTTPS Only**
   ```java
   tokenCookie.setSecure(true); // Only send over HTTPS
   ```

2. **CORS Configuration**
   ```java
   @Bean
   public CorsConfigurationSource corsConfigurationSource() {
       CorsConfiguration configuration = new CorsConfiguration();
       configuration.setAllowedOrigins(Arrays.asList("https://your-react-app.com"));
       configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE"));
       configuration.setAllowCredentials(true); // Important for cookies
       
       UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
       source.registerCorsConfiguration("/**", configuration);
       return source;
   }
   ```

3. **SameSite Cookie Attribute**
   ```java
   // Prevent CSRF attacks
   response.setHeader("Set-Cookie", 
       String.format("access_token=%s; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=%d",
       accessToken, expiresIn));
   ```

4. **Token Refresh**
   - Implement refresh token mechanism
   - Refresh before access token expires
   - Handle token refresh transparently in React

5. **Logout Mechanism**
   ```java
   @PostMapping("/api/logout")
   public ResponseEntity<?> logout(HttpServletResponse response) {
       Cookie cookie = new Cookie("access_token", null);
       cookie.setMaxAge(0);
       cookie.setPath("/");
       response.addCookie(cookie);
       return ResponseEntity.ok().build();
   }
   ```

---

## Complete Request Flow Diagram

```
USER                   REACT APP              SPRING BACKEND            KEYCLOAK
 |                         |                         |                      |
 |-- Click "Login" ------->|                         |                      |
 |                         |-- GET /api/protected -->|                      |
 |                         |                         |-- No token found     |
 |                         |<------ 302 redirect ----|                      |
 |                         |                         |                      |
 |<----- Redirect to Keycloak login page ------------------------------ ----|
 |                         |                         |                      |
 |-- Enter credentials ------------------------------------------->|
 |                         |                         |                      |
 |<----- Redirect to /oauth2/callback?code=ABC ---------------------|
 |                         |                         |                      |
 |                         |                         |<-- Receive code      |
 |                         |                         |-- POST /token ------>|
 |                         |                         |<-- Access token -----|
 |                         |                         |-- Set cookie         |
 |                         |<------ Redirect --------|                      |
 |                         |    /api/user-info       |                      |
 |                         |     + cookie            |                      |
 |                         |                         |                      |
 |                         |-- GET /api/user-info -->|                      |
 |                         |     (cookie included)   |                      |
 |                         |                         |-- Extract token      |
 |                         |                         |-- Validate JWT       |
 |                         |<------ User info -------|                      |
 |<----- Display profile --|                         |                      |
 |                         |                         |                      |
 |                         |-- GET /api/data ------->|                      |
 |                         |     (cookie included)   |                      |
 |                         |                         |-- Extract token      |
 |                         |                         |-- Validate JWT       |
 |                         |<------ Data ------------|                      |
```

---

## Debugging Tips

### Common Issues and Solutions

1. **CORS Errors in React**
   - Ensure `credentials: 'include'` in fetch
   - Configure CORS in Spring to allow credentials
   - Set `allowCredentials: true`

2. **Cookie Not Being Sent**
   - Check that domain matches between backend and frontend
   - Verify `credentials: 'include'` in all fetch calls
   - Check browser dev tools → Application → Cookies

3. **Token Validation Failing**
   - Verify Keycloak issuer matches configuration
   - Check token hasn't expired
   - Ensure Keycloak realm public keys are accessible

4. **Redirect Loop**
   - Verify `/oauth2/callback` is in `permitAll()` list
   - Check redirect_uri matches exactly in Keycloak config
   - Ensure cookie is being set correctly

5. **401 Unauthorized Errors**
   - Check token is in cookie
   - Verify cookie filter is running
   - Check JWT validation configuration

---

## Conclusion

This OAuth2 implementation provides:
- Secure authentication using industry-standard protocols
- HttpOnly cookie-based token storage (prevents XSS)
- Stateless architecture (no server-side sessions)
- Seamless integration with React (automatic cookie handling)
- Centralized authentication with Keycloak

The key advantage is that React doesn't need to manage tokens manually—the browser handles everything automatically through cookies, making the implementation cleaner and more secure.

# OAuth2 Security: MITM Protection & Cookie Alternatives

## Table of Contents
1. [Man-in-the-Middle (MITM) Attack Overview](#mitm-attack-overview)
2. [Protection Mechanisms](#protection-mechanisms)
3. [Are Cookies Required?](#are-cookies-required)
4. [Token Storage Alternatives](#token-storage-alternatives)
5. [Security Comparison](#security-comparison)
6. [Implementation Examples](#implementation-examples)
7. [Best Practices](#best-practices)

---

## Man-in-the-Middle (MITM) Attack Overview

### What is a MITM Attack?

A Man-in-the-Middle attack occurs when an attacker intercepts communication between two parties:

```
USER <----[ATTACKER]----> SERVER
```

### MITM Attack Vectors in OAuth2

#### 1. **Authorization Code Interception**
```
User → Keycloak: Login successful
Keycloak → User: Redirect to /callback?code=ABC123
ATTACKER intercepts: code=ABC123
Attacker → Backend: /callback?code=ABC123
Backend → Attacker: Access Token (COMPROMISED)
```

#### 2. **Token Theft in Transit**
```
Backend → User: Set-Cookie: access_token=JWT_TOKEN
ATTACKER intercepts: JWT_TOKEN
Attacker can now: Impersonate user with stolen token
```

#### 3. **Redirect URI Manipulation**
```
User clicks: Login
Attacker modifies: redirect_uri=https://evil.com
Keycloak redirects to: https://evil.com?code=ABC123
Attacker: Steals authorization code
```

#### 4. **SSL Stripping**
```
User requests: https://yourapp.com
Attacker downgrades: http://yourapp.com (no encryption)
All traffic: Visible to attacker
```

---

## Protection Mechanisms

### 1. HTTPS/TLS (Mandatory)

**What it does:**
- Encrypts all data in transit
- Prevents eavesdropping and tampering
- Validates server identity via certificates

**Implementation:**

```java
// SecurityConfig.java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .requiresChannel(channel -> channel
            .anyRequest().requiresSecure() // Force HTTPS
        )
        // ... rest of config
}
```

**Cookie Configuration:**
```java
Cookie tokenCookie = new Cookie("access_token", accessToken);
tokenCookie.setSecure(true);  // ⚠️ CRITICAL: Only sent over HTTPS
tokenCookie.setHttpOnly(true); // Prevents JavaScript access
```

**Spring Boot application.properties:**
```properties
# Force HTTPS
server.ssl.enabled=true
server.ssl.key-store=classpath:keystore.p12
server.ssl.key-store-password=your-password
server.ssl.key-store-type=PKCS12
server.ssl.key-alias=tomcat

# Redirect HTTP to HTTPS
server.port=8443
```

**Key Points:**
- Without HTTPS, ALL OAuth2 security is meaningless
- Use valid SSL certificates (not self-signed in production)
- TLS 1.2 or higher required
- Strong cipher suites only

---

### 2. PKCE (Proof Key for Code Exchange)

**What it does:**
- Prevents authorization code interception attacks
- Even if code is stolen, attacker can't exchange it for token
- Required for mobile/SPA apps, recommended for all

**How PKCE Works:**

```
Step 1: Client generates random code_verifier
  code_verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"

Step 2: Client creates code_challenge from verifier
  code_challenge = BASE64URL(SHA256(code_verifier))
  code_challenge = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"

Step 3: Authorization request includes challenge
  /auth?client_id=app
       &redirect_uri=http://localhost/callback
       &response_type=code
       &code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
       &code_challenge_method=S256

Step 4: Keycloak stores challenge with code

Step 5: Token exchange includes original verifier
  POST /token
  grant_type=authorization_code
  &code=AUTH_CODE
  &redirect_uri=http://localhost/callback
  &code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk

Step 6: Keycloak verifies: SHA256(code_verifier) == code_challenge
  ✅ Match: Issue token
  ❌ No match: Reject (code was stolen)
```

**Java Implementation:**

```java
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

public class PKCEUtil {
    
    // Generate random code verifier
    public static String generateCodeVerifier() {
        SecureRandom secureRandom = new SecureRandom();
        byte[] code = new byte[32];
        secureRandom.nextBytes(code);
        return Base64.getUrlEncoder()
            .withoutPadding()
            .encodeToString(code);
    }
    
    // Generate code challenge from verifier
    public static String generateCodeChallenge(String codeVerifier) {
        try {
            byte[] bytes = codeVerifier.getBytes("US-ASCII");
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(bytes);
            byte[] digest = md.digest();
            return Base64.getUrlEncoder()
                .withoutPadding()
                .encodeToString(digest);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

**Updated SecurityConfig with PKCE:**

```java
@Bean
public AuthenticationEntryPoint keycloakAuthenticationEntryPoint() {
    return (request, response, authException) -> {
        // Generate PKCE parameters
        String codeVerifier = PKCEUtil.generateCodeVerifier();
        String codeChallenge = PKCEUtil.generateCodeChallenge(codeVerifier);
        
        // Store verifier in session (will need for token exchange)
        request.getSession().setAttribute("code_verifier", codeVerifier);
        
        String authorizationUrl = String.format(
            "%s/realms/%s/protocol/openid-connect/auth?client_id=%s&redirect_uri=%s&response_type=code&scope=openid&code_challenge=%s&code_challenge_method=S256",
            keycloakUrl, realm, clientId, redirectUri, codeChallenge
        );
        response.sendRedirect(authorizationUrl);
    };
}
```

**Updated OAuth2CallbackController with PKCE:**

```java
@GetMapping("/oauth2/callback")
public void handleCallback(
        @RequestParam("code") String code,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {
    
    // Retrieve stored code verifier
    String codeVerifier = (String) request.getSession().getAttribute("code_verifier");
    request.getSession().removeAttribute("code_verifier");
    
    // Token exchange with PKCE
    MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
    body.add("grant_type", "authorization_code");
    body.add("client_id", clientId);
    body.add("code", code);
    body.add("redirect_uri", redirectUri);
    body.add("code_verifier", codeVerifier); // ⚠️ Include verifier
    
    // ... rest of token exchange
}
```

**Why PKCE Matters:**
- Even if attacker intercepts authorization code, they can't use it
- They don't have the original code_verifier
- Keycloak validates verifier matches challenge before issuing token

---

### 3. State Parameter (CSRF Protection)

**What it does:**
- Prevents Cross-Site Request Forgery (CSRF)
- Validates callback request originated from your app
- Ties OAuth request to user session

**Implementation:**

```java
@Bean
public AuthenticationEntryPoint keycloakAuthenticationEntryPoint() {
    return (request, response, authException) -> {
        // Generate random state token
        String state = UUID.randomUUID().toString();
        
        // Store in session
        request.getSession().setAttribute("oauth_state", state);
        
        String authorizationUrl = String.format(
            "%s/realms/%s/protocol/openid-connect/auth?client_id=%s&redirect_uri=%s&response_type=code&scope=openid&state=%s",
            keycloakUrl, realm, clientId, redirectUri, state
        );
        response.sendRedirect(authorizationUrl);
    };
}
```

```java
@GetMapping("/oauth2/callback")
public void handleCallback(
        @RequestParam("code") String code,
        @RequestParam("state") String state,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {
    
    // Validate state parameter
    String sessionState = (String) request.getSession().getAttribute("oauth_state");
    if (sessionState == null || !sessionState.equals(state)) {
        response.sendError(HttpServletResponse.SC_BAD_REQUEST, "Invalid state parameter");
        return;
    }
    request.getSession().removeAttribute("oauth_state");
    
    // Proceed with token exchange...
}
```

**Attack Scenario Prevented:**
```
1. Attacker initiates OAuth on their device
2. Keycloak redirects: /callback?code=ATTACKER_CODE&state=ATTACKER_STATE
3. Attacker tricks victim to visit: yourapp.com/callback?code=ATTACKER_CODE&state=ATTACKER_STATE
4. Your app checks: state != session_state
5. ❌ Request rejected (states don't match)
```

---

### 4. Strict Redirect URI Validation

**What it does:**
- Prevents redirect to malicious sites
- Keycloak validates redirect_uri exactly matches registered value

**Keycloak Configuration:**
```
Client Settings:
  Valid Redirect URIs: https://yourapp.com/oauth2/callback (exact match)
  
❌ Will reject: https://evil.com/steal
❌ Will reject: https://yourapp.com.evil.com/callback
❌ Will reject: https://yourapp.com/oauth2/callback/../evil
✅ Will accept: https://yourapp.com/oauth2/callback
```

**Backend Validation:**
```java
@Value("${keycloak.redirect-uri}")
private String redirectUri;

// In token exchange
body.add("redirect_uri", redirectUri); // Must match exactly
```

---

### 5. Token Expiration & Rotation

**Short-lived Access Tokens:**
```properties
# Keycloak settings
Access Token Lifespan: 15 minutes (not 24 hours!)
Refresh Token Lifespan: 30 minutes
```

**Benefits:**
- If token is stolen, damage window is limited
- Token becomes useless after expiration
- Forces periodic re-authentication

**Implementation:**
```java
Cookie tokenCookie = new Cookie("access_token", accessToken);
tokenCookie.setMaxAge(expiresIn); // Token expires with cookie
```

---

### 6. Certificate Pinning (Advanced)

**What it does:**
- App only trusts specific SSL certificates
- Prevents rogue Certificate Authority attacks

**Implementation:**
```java
@Bean
public RestTemplate restTemplate() throws Exception {
    SSLContext sslContext = SSLContextBuilder
        .create()
        .loadTrustMaterial(
            ResourceUtils.getFile("classpath:keycloak-cert.pem"),
            null
        )
        .build();
    
    SSLConnectionSocketFactory socketFactory = 
        new SSLConnectionSocketFactory(sslContext);
    
    HttpClient httpClient = HttpClients.custom()
        .setSSLSocketFactory(socketFactory)
        .build();
    
    HttpComponentsClientHttpRequestFactory factory = 
        new HttpComponentsClientHttpRequestFactory(httpClient);
    
    return new RestTemplate(factory);
}
```

**Warning:** Requires careful certificate management and rotation

---

### 7. Content Security Policy (CSP)

**What it does:**
- Prevents injection of malicious scripts
- Restricts where resources can be loaded from

**Implementation:**
```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .headers(headers -> headers
            .contentSecurityPolicy(csp -> csp
                .policyDirectives("default-src 'self'; script-src 'self'; style-src 'self'")
            )
        );
}
```

---

## Are Cookies Required?

### Short Answer: **NO, cookies are NOT required**

Your current implementation uses cookies for convenience and security, but there are multiple alternatives.

### Why Your Implementation Uses Cookies

**Advantages:**
1. **Automatic management** - Browser sends cookie with every request
2. **HttpOnly flag** - JavaScript cannot access (XSS protection)
3. **Secure flag** - Only sent over HTTPS (MITM protection)
4. **SameSite attribute** - CSRF protection
5. **No client-side code** - React doesn't manage tokens

**Disadvantages:**
1. **CORS complexity** - Need `credentials: 'include'` and CORS config
2. **Mobile apps** - Cookies not ideal for native mobile
3. **Third-party cookies** - Being deprecated in browsers
4. **Cookie size limits** - 4KB limit per cookie

---

## Token Storage Alternatives

### Option 1: Authorization Header (Recommended for APIs)

**How it works:**
- React stores token in memory
- Manually adds `Authorization: Bearer <token>` header to each request
- No cookies involved

**Backend Changes:**

```java
// Remove cookie filter entirely
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        // NO cookieToHeaderFilter needed
        .authorizeHttpRequests(authz -> authz
            .requestMatchers("/oauth2/callback", "/error").permitAll()
            .anyRequest().authenticated()
        )
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt() // Still validates JWT from Authorization header
        )
        .csrf(csrf -> csrf.disable());
    
    return http.build();
}
```

**OAuth2CallbackController Changes:**

```java
@GetMapping("/oauth2/callback")
public ResponseEntity<?> handleCallback(
        @RequestParam("code") String code,
        HttpServletResponse response) throws Exception {
    
    // Exchange code for token (same as before)
    // ...
    
    String accessToken = (String) tokenResponse.getBody().get("access_token");
    String refreshToken = (String) tokenResponse.getBody().get("refresh_token");
    Integer expiresIn = (Integer) tokenResponse.getBody().get("expires_in");
    
    // Return tokens in JSON response (no cookies)
    Map<String, Object> tokens = new HashMap<>();
    tokens.put("access_token", accessToken);
    tokens.put("refresh_token", refreshToken);
    tokens.put("expires_in", expiresIn);
    
    return ResponseEntity.ok(tokens);
}
```

**React Implementation:**

```javascript
// AuthContext.js
import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [user, setUser] = useState(null);

  const login = async (code) => {
    try {
      // Exchange code for token
      const response = await fetch(`http://localhost:8080/oauth2/callback?code=${code}`);
      const data = await response.json();
      
      // Store token in memory (or localStorage if needed)
      setAccessToken(data.access_token);
      
      // Optionally store refresh token
      localStorage.setItem('refresh_token', data.refresh_token);
      
      // Fetch user info
      await fetchUserInfo(data.access_token);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const fetchUserInfo = async (token) => {
    const response = await fetch('http://localhost:8080/api/user-info', {
      headers: {
        'Authorization': `Bearer ${token}`, // Manual header
        'Accept': 'application/json',
      }
    });
    
    if (response.ok) {
      const userData = await response.json();
      setUser(userData);
    }
  };

  const logout = () => {
    setAccessToken(null);
    setUser(null);
    localStorage.removeItem('refresh_token');
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

**API Client with Authorization Header:**

```javascript
// api.js
export const apiClient = {
  async get(endpoint, token) {
    const response = await fetch(`http://localhost:8080/api${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${token}`, // Manual token
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async post(endpoint, data, token) {
    const response = await fetch(`http://localhost:8080/api${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`, // Manual token
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
};

// Usage
function UserProfile() {
  const { accessToken } = useAuth();
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (accessToken) {
      apiClient.get('/user-info', accessToken)
        .then(setUser)
        .catch(console.error);
    }
  }, [accessToken]);

  return <div>{user?.name}</div>;
}
```

**Pros:**
- ✅ Simple backend (no custom filter)
- ✅ No CORS credential issues
- ✅ Works for mobile apps
- ✅ Standard REST API pattern
- ✅ Token visible for debugging

**Cons:**
- ❌ React must manage token in memory
- ❌ Token can be accessed by JavaScript (XSS risk)
- ❌ Must manually add header to each request
- ❌ Token lost on page refresh (unless stored somewhere)

---

### Option 2: localStorage (Common but Less Secure)

**How it works:**
- Store token in browser's localStorage
- Persists across page refreshes and sessions
- Manually add to Authorization header

**React Implementation:**

```javascript
// AuthContext.js
export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(
    localStorage.getItem('access_token')
  );

  const login = async (code) => {
    const response = await fetch(`http://localhost:8080/oauth2/callback?code=${code}`);
    const data = await response.json();
    
    // Store in localStorage
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    setAccessToken(data.access_token);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAccessToken(null);
  };

  // Check for token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Validate token is still valid
      validateToken(token);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ accessToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

**Pros:**
- ✅ Persists across page refreshes
- ✅ Simple to implement
- ✅ No server-side session needed
- ✅ Works across tabs

**Cons:**
- ❌ Vulnerable to XSS attacks
- ❌ Accessible by any JavaScript (including malicious scripts)
- ❌ Not automatically sent with requests
- ❌ No protection from JavaScript access

---

### Option 3: sessionStorage (Better than localStorage)

**How it works:**
- Similar to localStorage but cleared when tab closes
- Shorter lifetime = reduced risk

**Implementation:**

```javascript
// Use sessionStorage instead
sessionStorage.setItem('access_token', data.access_token);
const token = sessionStorage.getItem('access_token');
sessionStorage.removeItem('access_token');
```

**Pros:**
- ✅ Cleared when tab closes
- ✅ Not shared across tabs
- ✅ Simpler than cookies

**Cons:**
- ❌ Still vulnerable to XSS
- ❌ Lost on tab close
- ❌ Accessible by JavaScript

---

### Option 4: Memory Only (Most Secure, No Persistence)

**How it works:**
- Store token only in React state
- Never persisted anywhere
- Lost on page refresh

**Implementation:**

```javascript
export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null); // Memory only

  // No persistence - token lost on refresh
}
```

**Pros:**
- ✅ Most secure (not persisted)
- ✅ Can't be stolen if user leaves computer
- ✅ No XSS risk for long-term storage

**Cons:**
- ❌ Lost on page refresh (bad UX)
- ❌ User must re-login frequently
- ❌ Not practical for most apps

---

### Option 5: Hybrid Approach (Recommended)

**How it works:**
- Store refresh token in HttpOnly cookie
- Store access token in memory
- Use refresh token to get new access token

**Backend:**

```java
@GetMapping("/oauth2/callback")
public ResponseEntity<?> handleCallback(
        @RequestParam("code") String code,
        HttpServletResponse response) throws Exception {
    
    // Exchange code for tokens
    String accessToken = (String) tokenResponse.getBody().get("access_token");
    String refreshToken = (String) tokenResponse.getBody().get("refresh_token");
    Integer expiresIn = (Integer) tokenResponse.getBody().get("expires_in");
    
    // Store REFRESH token in HttpOnly cookie (secure)
    Cookie refreshCookie = new Cookie("refresh_token", refreshToken);
    refreshCookie.setHttpOnly(true);
    refreshCookie.setSecure(true);
    refreshCookie.setPath("/");
    refreshCookie.setMaxAge(30 * 24 * 60 * 60); // 30 days
    response.addCookie(refreshCookie);
    
    // Return ACCESS token in JSON (short-lived)
    Map<String, Object> tokens = new HashMap<>();
    tokens.put("access_token", accessToken);
    tokens.put("expires_in", expiresIn);
    
    return ResponseEntity.ok(tokens);
}

@PostMapping("/api/refresh")
public ResponseEntity<?> refresh(HttpServletRequest request) {
    // Extract refresh token from cookie
    Cookie[] cookies = request.getCookies();
    String refreshToken = null;
    
    if (cookies != null) {
        for (Cookie cookie : cookies) {
            if ("refresh_token".equals(cookie.getName())) {
                refreshToken = cookie.getValue();
                break;
            }
        }
    }
    
    if (refreshToken == null) {
        return ResponseEntity.status(401).body("No refresh token");
    }
    
    // Exchange refresh token for new access token
    // ... call Keycloak token endpoint with grant_type=refresh_token
    
    Map<String, Object> tokens = new HashMap<>();
    tokens.put("access_token", newAccessToken);
    tokens.put("expires_in", expiresIn);
    
    return ResponseEntity.ok(tokens);
}
```

**React:**

```javascript
export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null); // Memory only

  const refreshAccessToken = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/refresh', {
        method: 'POST',
        credentials: 'include', // Send refresh token cookie
      });
      
      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access_token);
        return data.access_token;
      } else {
        // Refresh token expired, need to re-login
        logout();
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
    }
  };

  // Auto-refresh before expiration
  useEffect(() => {
    if (accessToken) {
      const interval = setInterval(() => {
        refreshAccessToken();
      }, 14 * 60 * 1000); // Refresh every 14 minutes (token expires at 15)
      
      return () => clearInterval(interval);
    }
  }, [accessToken]);

  return (
    <AuthContext.Provider value={{ accessToken, refreshAccessToken, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

**Pros:**
- ✅ Access token not persisted (XSS safe)
- ✅ Refresh token in HttpOnly cookie (secure)
- ✅ Automatic token refresh
- ✅ Good UX (no frequent re-logins)
- ✅ Best of both worlds

**Cons:**
- ❌ More complex implementation
- ❌ Still need CORS for refresh endpoint

---

## Security Comparison

| Storage Method | XSS Protection | CSRF Protection | MITM Protection | Persistence | Complexity |
|---------------|----------------|-----------------|-----------------|-------------|------------|
| **HttpOnly Cookie** | ✅ Excellent | ⚠️ Need SameSite | ✅ With Secure flag | ✅ Yes | Medium |
| **Authorization Header + Memory** | ⚠️ If no storage | ✅ N/A | ✅ With HTTPS | ❌ No | Low |
| **localStorage** | ❌ Vulnerable | ✅ N/A | ✅ With HTTPS | ✅ Yes | Low |
| **sessionStorage** | ❌ Vulnerable | ✅ N/A | ✅ With HTTPS | ⚠️ Tab only | Low |
| **Hybrid (Recommended)** | ✅ Excellent | ⚠️ Need SameSite | ✅ With HTTPS | ✅ Yes | High |

---

## Implementation Examples

### Complete Hybrid Implementation

**Backend (Spring Boot):**

```java
// SecurityConfig.java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers(
                    "/oauth2/callback",
                    "/api/refresh",
                    "/error"
                ).permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt() // Validates Bearer token from Authorization header
            )
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                .ignoringRequestMatchers("/api/refresh") // Allow refresh without CSRF
            );
        
        return http.build();
    }
}

// OAuth2CallbackController.java
@RestController
public class OAuth2CallbackController {
    
    @GetMapping("/oauth2/callback")
    public ResponseEntity<?> handleCallback(
            @RequestParam("code") String code,
            @RequestParam("state") String state,
            HttpServletRequest request,
            HttpServletResponse response) throws Exception {
        
        // Validate state (CSRF protection)
        String sessionState = (String) request.getSession().getAttribute("oauth_state");
        if (!state.equals(sessionState)) {
            return ResponseEntity.badRequest().body("Invalid state");
        }
        
        // Exchange code for tokens (with PKCE)
        String codeVerifier = (String) request.getSession().getAttribute("code_verifier");
        Map<String, Object> tokenResponse = exchangeCodeForToken(code, codeVerifier);
        
        String accessToken = (String) tokenResponse.get("access_token");
        String refreshToken = (String) tokenResponse.get("refresh_token");
        Integer expiresIn = (Integer) tokenResponse.get("expires_in");
        
        // Store refresh token in secure cookie
        Cookie refreshCookie = new Cookie("refresh_token", refreshToken);
        refreshCookie.setHttpOnly(true);
        refreshCookie.setSecure(true);
        refreshCookie.setSameSite("Strict");
        refreshCookie.setPath("/");
        refreshCookie.setMaxAge(30 * 24 * 60 * 60); // 30 days
        response.addCookie(refreshCookie);
        
        // Return access token in response
        Map<String, Object> result = new HashMap<>();
        result.put("access_token", accessToken);
        result.put("expires_in", expiresIn);
        result.put("token_type", "Bearer");
        
        return ResponseEntity.ok(result);
    }
    
    @PostMapping("/api/refresh")
    public ResponseEntity<?> refreshToken(HttpServletRequest request) {
        // Extract refresh token from cookie
        String refreshToken = extractRefreshToken(request);
        
        if (refreshToken == null) {
            return ResponseEntity.status(401).body("No refresh token");
        }
        
        try {
            // Exchange refresh token for new access token
            Map<String, Object> tokenResponse = refreshAccessToken(refreshToken);
            
            String newAccessToken = (String) tokenResponse.get("access_token");
            Integer expiresIn = (Integer) tokenResponse.get("expires_in");
            
            Map<String, Object> result = new HashMap<>();
            result.put("access_token", newAccessToken);
            result.put("expires_in", expiresIn);
            result.put("token_type", "Bearer");
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            return ResponseEntity.status(401).body("Token refresh failed");
        }
    }
    
    private Map<String, Object> refreshAccessToken(String refreshToken) {
        String tokenEndpoint = String.format(
            "%s/realms/%s/protocol/openid-connect/token",
            keycloakUrl, realm
        );
        
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
        
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("grant_type", "refresh_token");
        body.add("client_id", clientId);
        body.add("client_secret", clientSecret);
        body.add("refresh_token", refreshToken);
        
        HttpEntity<MultiValueMap<String, String>> request = 
            new HttpEntity<>(body, headers);
            
        ResponseEntity<Map> response = restTemplate.postForEntity(
            tokenEndpoint, request, Map.class
        );
        
        return response.getBody();
    }
}
```

**React Implementation:**

```javascript
// api.js
export class ApiClient {
  constructor() {
    this.baseURL = 'http://localhost:8080/api';
    this.accessToken = null;
    this.refreshPromise = null;
  }

  setAccessToken(token) {
    this.accessToken = token;
  }

  async refreshAccessToken() {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = fetch('http://localhost:8080/api/refresh', {
      method: 'POST',
      credentials: 'include', // Send refresh token cookie
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Token refresh failed');
        }
        return response.json();
      })
      .then(data => {
        this.accessToken = data.access_token;
        this.refreshPromise = null;
        return data.access_token;
      })
      .catch(error => {
        this.refreshPromise = null;
        throw error;
      });

    return this.refreshPromise;
  }

  async request(endpoint, options = {}) {
    // Add Authorization header
    const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    let response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    // If unauthorized, try refreshing token
    if (response.status === 401 && this.accessToken) {
      try {
        await this.refreshAccessToken();
        
        // Retry original request with new token
        headers['Authorization'] = `Bearer ${this.accessToken}`;
        response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers,
        });
      } catch (error) {
        // Refresh failed, user needs to re-login
        throw new Error('Session expired. Please login again.');
      }
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient();
```

---

## Best Practices

### 1. Always Use HTTPS in Production

```properties
# application.properties
server.ssl.enabled=true
server.port=8443
```

### 2. Implement PKCE for All OAuth Flows

```java
// Always include code_challenge
&code_challenge=${challenge}
&code_challenge_method=S256
```

### 3. Use State Parameter

```java
// Always validate state matches
if (!state.equals(sessionState)) {
    throw new SecurityException("State mismatch");
}
```

### 4. Short Token Lifetimes

```
Access Token: 15 minutes
Refresh Token: 30 days
```

### 5. Implement Token Refresh

```javascript
// Auto-refresh before expiration
setInterval(refreshToken, 14 * 60 * 1000);
```

### 6. Validate Redirect URIs

```java
// Whitelist exact URIs
@Value("${keycloak.redirect-uri}")
private String redirectUri; // Must match Keycloak config
```

### 7. Use SameSite Cookies

```java
cookie.setSameSite("Strict"); // or "Lax"
```

### 8. Implement Logout

```java
@PostMapping("/api/logout")
public ResponseEntity<?> logout(HttpServletResponse response) {
    // Clear refresh token cookie
    Cookie cookie = new Cookie("refresh_token", null);
    cookie.setMaxAge(0);
    cookie.setPath("/");
    response.addCookie(cookie);
    
    // Optionally revoke token at Keycloak
    // ...
    
    return ResponseEntity.ok().build();
}
```

### 9. Monitor for Token Theft

```java
// Log all token usage
@Component
public class TokenAuditFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                   HttpServletResponse response, 
                                   FilterChain filterChain) {
        // Log IP, user-agent, timestamp
        // Alert on suspicious patterns (multiple IPs, locations)
    }
}
```

### 10. Rate Limiting

```java
@Bean
public RateLimiter rateLimiter() {
    return RateLimiter.create(10.0); // 10 requests per second
}
```

---

## Summary

### MITM Protection Checklist

✅ **Mandatory:**
- HTTPS/TLS for all communication
- Valid SSL certificates
- State parameter (CSRF protection)
- Strict redirect URI validation
- Short token lifetimes

✅ **Highly Recommended:**
- PKCE implementation
- Token refresh mechanism
- SameSite cookies
- Content Security Policy

✅ **Advanced:**
- Certificate pinning
- Token binding
- Anomaly detection

### Cookie Alternatives

**Use Cookies when:**
- Building traditional web app
- Want automatic token management
- Need HttpOnly protection
- Backend and frontend same domain

**Use Authorization Header when:**
- Building mobile app
- Microservices architecture
- Frontend and backend different domains
- Need more control over token storage

**Use Hybrid Approach when:**
- Need best security
- Want good UX
- Can handle complexity
- Building production app

**The key to security isn't the storage method alone—it's the combination of HTTPS, PKCE, proper validation, and defense in depth.**