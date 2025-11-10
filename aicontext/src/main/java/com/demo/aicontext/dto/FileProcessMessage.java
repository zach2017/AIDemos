package com.demo.aicontext.dto;


import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

// Message for SQS
@Data
@NoArgsConstructor
@AllArgsConstructor
public class FileProcessMessage {
    private String fileKey;
    private String bucketName;
    private String originalFileName;
    private long fileSize;
    private String userId;
}
