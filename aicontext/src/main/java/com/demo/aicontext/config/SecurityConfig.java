package com.demo.aicontext.config;
// SecurityConfig.java
// SecurityConfig.java - Updated to permit static resources
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Value("${keycloak.auth-server-url}")
    private String keycloakUrl;
    
    @Value("${keycloak.realm}")
    private String realm;
    
    @Value("${keycloak.client-id}")
    private String clientId;
    
    @Value("${keycloak.redirect-uri}")
    private String redirectUri;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .addFilterBefore(cookieToHeaderFilter(), UsernamePasswordAuthenticationFilter.class)
            .authorizeHttpRequests(authz -> authz
                .requestMatchers(  
                    "/oauth2/callback",      
                    "/error"                   
                ).permitAll()
                .requestMatchers("**").authenticated()  
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt()
                .and()
                .authenticationEntryPoint(keycloakAuthenticationEntryPoint())
            )
            .csrf(csrf -> csrf.disable()); // Disable CSRF for API endpoints
        
        return http.build();
    }
    
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
    
    @Bean
    public OncePerRequestFilter cookieToHeaderFilter() {
        return new OncePerRequestFilter() {
            @Override
            protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, 
                                          FilterChain filterChain) throws ServletException, IOException {
                
                // Only process API requests
                if (request.getRequestURI().startsWith("/api")) {
                    // Extract token from cookie and add to Authorization header
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
}

class HttpServletRequestWrapper extends jakarta.servlet.http.HttpServletRequestWrapper {
    public HttpServletRequestWrapper(HttpServletRequest request) {
        super(request);
    }
}
