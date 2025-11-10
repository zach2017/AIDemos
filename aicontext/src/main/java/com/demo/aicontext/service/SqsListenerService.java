package com.demo.aicontext.service;

import io.awspring.cloud.sqs.annotation.SqsListener;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import com.demo.aicontext.dto.FileProcessMessage;
import com.demo.aicontext.dto.StatusUpdate;

import io.awspring.cloud.sqs.operations.SqsTemplate;

@Service
@RequiredArgsConstructor
@Slf4j
public class SqsListenerService {

    private final SqsTemplate sqsTemplate;
    private final SimpMessagingTemplate websocketTemplate;

    @Value("${aws.sqs.finished-queue}")
    private String finishedQueueName;

    @Value("${aws.sqs.malware-queue}")
    private String malwareQueueName;

    @SqsListener(queueNames = "${aws.sqs.pending-queue}")
    public void handlePendingFile(FileProcessMessage message) throws InterruptedException {
        log.info("Processing message for file: {}", message.getOriginalFileName());
        
        // --- Simulate Guarddog Malware Scan ---
        // Guarddog is a Python tool for CI/CD. Here, we simulate the *intent*
        // (malware scanning) by checking the file name.
        boolean isMalware = simulateMalwareScan(message.getOriginalFileName());
        // ----------------------------------------

        String userId = message.getUserId();
        StatusUpdate status;

        if (isMalware) {
            log.warn("Malware detected in file: {}", message.getOriginalFileName());
            status = new StatusUpdate("MALWARE_DETECTED", message.getOriginalFileName(), message.getFileSize());
            // Send to malware queue
            sqsTemplate.send(malwareQueueName, message);
        } else {
            log.info("File {} processed successfully.", message.getOriginalFileName());
            status = new StatusUpdate("PROCESSED", message.getOriginalFileName(), message.getFileSize());
            // Send to finished queue
            sqsTemplate.send(finishedQueueName, message);
        }

        // Send WebSocket update to the specific user
        websocketTemplate.convertAndSend("/topic/status." + userId, status);
    }

    private boolean simulateMalwareScan(String fileName) throws InterruptedException {
        // Simulate a scan that takes time
        Thread.sleep(3000); // 3-second "scan"
        
        // Simulating a positive hit on a "eicar" test file
        return fileName.toLowerCase().contains("eicar");
    }
}
