package com.demo.aicontext.controller;

import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.extern.slf4j.Slf4j;

// UserInfoController.java (separate controller for user info endpoint)
@RestController
@RequestMapping("/api")
@Slf4j
public class UserInfoController {
    
    @GetMapping("/user-info")
    public ResponseEntity<Map<String, Object>> getUserInfo(@AuthenticationPrincipal Jwt jwt) {
        log.info(jwt.getClaimAsString("preferred_username"));
        return ResponseEntity.ok(Map.of(
            "username", jwt.getClaimAsString("preferred_username"),
            "email", jwt.getClaimAsString("email"),
            "subject", jwt.getSubject()
        ));
    }
}