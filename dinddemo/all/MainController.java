package com.example.springdockerapp.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.SendMessageRequest;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class MainController {

    @Autowired
    private S3Client s3Client;

    @Autowired
    private SqsClient sqsClient;

    private final String bucketName = "test-bucket";
    private final String queueUrl = "http://localstack:4566/000000000000/test-queue";

    @GetMapping("/public/health")
    public Map<String, String> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        response.put("message", "Application is running");
        return response;
    }

    @GetMapping("/user/info")
    public Map<String, String> getUserInfo() {
        Map<String, String> response = new HashMap<>();
        response.put("message", "Authenticated user endpoint");
        response.put("status", "success");
        return response;
    }

    @PostMapping("/user/upload")
    public Map<String, String> uploadToS3(@RequestParam String fileName, @RequestBody String content) {
        try {
            PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(fileName)
                .build();

            s3Client.putObject(putObjectRequest, RequestBody.fromString(content));

            Map<String, String> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "File uploaded to S3");
            response.put("fileName", fileName);
            return response;
        } catch (Exception e) {
            Map<String, String> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", e.getMessage());
            return response;
        }
    }

    @PostMapping("/user/message")
    public Map<String, String> sendMessage(@RequestBody String message) {
        try {
            SendMessageRequest sendMessageRequest = SendMessageRequest.builder()
                .queueUrl(queueUrl)
                .messageBody(message)
                .build();

            sqsClient.sendMessage(sendMessageRequest);

            Map<String, String> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Message sent to SQS");
            return response;
        } catch (Exception e) {
            Map<String, String> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", e.getMessage());
            return response;
        }
    }
}
