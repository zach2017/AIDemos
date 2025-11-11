package com.demo.aicontext.controller;
// OAuth2CallbackController.java

// OAuth2CallbackController.java - Add better error handling
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
import java.util.Map;

@RestController
public class OAuth2CallbackController {

    @Value("${keycloak.auth-server-url}")
    private String keycloakUrl;
    
    @Value("${keycloak.realm}")
    private String realm;
    
    @Value("${keycloak.client-id}")
    private String clientId;
    
    @Value("${keycloak.client-secret}")
    private String clientSecret;
    
    @Value("${keycloak.redirect-uri}")
    private String redirectUri;

    @GetMapping("/oauth2/callback")
    public void handleCallback(
            @RequestParam("code") String code,
            @RequestParam(value = "error", required = false) String error,
            @RequestParam(value = "error_description", required = false) String errorDescription,
            HttpServletResponse response) throws Exception {
        
        // Check for errors from Keycloak
        if (error != null) {
            response.sendError(HttpServletResponse.SC_BAD_REQUEST, 
                "OAuth2 Error: " + error + " - " + errorDescription);
            return;
        }
        
        try {
            // Exchange authorization code for access token
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
            
            String accessToken = (String) tokenResponse.getBody().get("access_token");
            Integer expiresIn = (Integer) tokenResponse.getBody().get("expires_in");
            
            // Store token in httpOnly cookie
            Cookie tokenCookie = new Cookie("access_token", accessToken);
            tokenCookie.setHttpOnly(true);
            tokenCookie.setSecure(false); // Set to true in production with HTTPS
            tokenCookie.setPath("/");
            tokenCookie.setMaxAge(expiresIn != null ? expiresIn : 3600);
            response.addCookie(tokenCookie);
            
            // Redirect to static upload page
            response.sendRedirect("/api/user-info");
            
        } catch (Exception e) {
            e.printStackTrace();
            response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, 
                "Failed to exchange authorization code: " + e.getMessage());
        }
    }
}