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