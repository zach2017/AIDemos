package com.demo.aicontext.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.demo.aicontext.service.FileUploadService;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class UploadController {

    private final FileUploadService fileUploadService;

    @PostMapping("/upload")
    public ResponseEntity<Map<String, String>> uploadFiles(
            @RequestParam("files") List<MultipartFile> files,
            @AuthenticationPrincipal Jwt jwt) {
        
        String userId = jwt.getSubject(); // Get user ID from Keycloak token
        Map<String, String> results = new ConcurrentHashMap<>();

        // Process all files asynchronously
        files.forEach(file -> {
            fileUploadService.processUpload(file, userId);
            results.put(file.getOriginalFilename(), "QUEUED");
        });

        return ResponseEntity.ok(results);
    }
}
