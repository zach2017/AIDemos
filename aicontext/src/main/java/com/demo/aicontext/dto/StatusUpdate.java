package com.demo.aicontext.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

// Message for WebSocket
@Data
@NoArgsConstructor
@AllArgsConstructor
public class StatusUpdate {
    private String status; // e.g., "PENDING", "PROCESSED", "MALWARE"
    private String fileName;
    private long fileSize;
}
