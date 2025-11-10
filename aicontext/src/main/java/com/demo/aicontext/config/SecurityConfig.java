package com.demo.aicontext.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeHttpRequests(authorize -> authorize
                        // Allow frontend, static assets, and WebSocket
                        .requestMatchers("/", "/index.html", "/ws/**").permitAll()
                        // Secure the API endpoint
                        .requestMatchers("/api/upload").authenticated()
                        .anyRequest().permitAll())
                .oauth2Login(Customizer.withDefaults()) // updated form
                .oauth2ResourceServer(rs -> rs
                        .jwt(Customizer.withDefaults()))
                .logout(logout -> logout
                        .logoutSuccessUrl("/"))
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .csrf(csrf -> csrf.disable()); // Disable CSRF for this stateless API

        return http.build();
    }
}
