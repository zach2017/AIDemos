package com.demo.aicontext.service;


import com.demo.aicontext.dto.FileProcessMessage;
import com.demo.aicontext.dto.StatusUpdate;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.awspring.cloud.sqs.operations.SqsTemplate;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

import java.util.UUID;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j
public class FileUploadService {

    private final S3Client s3Client;
    private final SqsTemplate sqsTemplate;
    private final SimpMessagingTemplate websocketTemplate;
    private final ObjectMapper objectMapper;

    @Value("${aws.s3.bucket-name}")
    private String bucketName;

    @Value("${aws.sqs.pending-queue}")
    private String pendingQueueName;

    @Async
    public CompletableFuture<Void> processUpload(MultipartFile file, String userId) {
        String originalFileName = file.getOriginalFilename();
        long fileSize = file.getSize();
        String fileKey = String.format("%s/%s-%s", userId, UUID.randomUUID(), originalFileName);

        try {
            // 1. Upload to S3
            log.info("Uploading file {} to S3 bucket {}", fileKey, bucketName);
            PutObjectRequest putReq = PutObjectRequest.builder()
                    .bucket(bucketName)
                    .key(fileKey)
                    .build();
            s3Client.putObject(putReq, RequestBody.fromInputStream(file.getInputStream(), fileSize));

            // 2. Send message to SQS pending-queue
            FileProcessMessage message = new FileProcessMessage(
                    fileKey, bucketName, originalFileName, fileSize, userId);
            
            sqsTemplate.send(pendingQueueName, message);
            log.info("Sent SQS message for file: {}", fileKey);

            // 3. Send WebSocket update
            StatusUpdate status = new StatusUpdate("PENDING", originalFileName, fileSize);
            websocketTemplate.convertAndSend("/topic/status." + userId, status);

        } catch (Exception e) {
            log.error("Error processing file upload for {}: {}", fileKey, e.getMessage(), e);
            // Optionally send an "ERROR" status via WebSocket
            StatusUpdate status = new StatusUpdate("ERROR", originalFileName, fileSize);
            websocketTemplate.convertAndSend("/topic/status." + userId, status);
        }
        
        return CompletableFuture.completedFuture(null);
    }
}
