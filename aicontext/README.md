Here is a detailed breakdown of each component, the end-to-end data flow, and a tutorial for using the application you've built.

-----

### Part 1: Component Explanations

This project is a **microservices-style architecture** orchestrated by Docker. Each component has a distinct and separate job.

#### 1\. Docker & `docker-compose.yml`

  * **What it is:** Docker is a platform for creating, deploying, and running applications in "containers." A container packages up code and all its dependencies. `docker-compose` is a tool for defining and running multi-container Docker applications (like ours).

  * **Role in this App:** The `docker-compose.yml` file is the "master script." It defines four services (`keycloak`, `localstack`, `spring-app`, `app-net`) and starts them all with a single command. It ensures they can all communicate with each other over a private network (`app-net`), allowing the Spring app to talk to `keycloak` and `localstack` by name.

  * **Key Concepts:**

      * **Containerization:** Isolates the app and its environment.
      * **Orchestration:** Manages multiple containers at once.
      * **Service Discovery:** Containers can find each other using their service names (e.g., `http://keycloak:8080`) instead of IP addresses.

#### 2\. Keycloak (Identity & Access Management)

  * **What it is:** An open-source Identity and Access Management (IAM) solution. It's a dedicated server that handles all things related to users: login, logout, registration, password management, and securing applications.

  * **Role in this App:** It acts as the "bouncer" for our application.

    1.  The `index.html` frontend redirects the user to Keycloak to log in.
    2.  Keycloak verifies the user's credentials (e.g., `user`/`password`).
    3.  It sends the user back to our app with a **JWT (JSON Web Token)**.
    4.  Our Spring Boot backend then validates this JWT on *every* API call to `/api/upload` to prove who the user is.

  * **Key Concepts:**

      * **Centralized Authentication:** Your app doesn't store passwords; Keycloak does.
      * **OAuth 2.0 / OpenID Connect (OIDC):** The standards used for this authentication flow.
      * **JWT (JSON Web Token):** A secure, signed "pass" that contains user information (like their User ID) and is given to the frontend to present to the backend.

#### 3\. LocalStack (AWS Services Emulator)

  * **What it is:** A powerful emulator that simulates Amazon Web Services (AWS) on your local machine. It allows you to write code against AWS APIs (like S3 and SQS) without needing an AWS account or an internet connection.

  * **Role in this App:** It provides two key services:

      * **S3 (Simple Storage Service):** Acts as our file storage. All uploaded documents are placed in the `document-bucket` here.
      * **SQS (Simple Queue Service):** Acts as our message bus. We use three queues:
          * `pending-queue`: A "to-do" list for the malware scanner.
          * `finished-queue`: An "inbox" for successfully scanned files.
          * `malware-queue`: An "inbox" for flagged, malicious files.

  * **Key Concepts:**

      * **Cloud Emulation:** A "fake" cloud for local development.
      * **Decoupling:** SQS decouples the initial upload from the processing. The `FileUploadService` doesn't know or care *when* the file is scanned; it just drops a message in the queue and moves on. This makes the app resilient.
      * **Infrastructure as Code:** The `.docker/localstack-init.sh` script automatically creates our bucket and queues on startup.

#### 4\. Spring Boot Backend (The Core Application)

  * **What it is:** The "brain" of the operation. This Java application runs all the custom business logic.

  * **Role in this App:** It's responsible for four main jobs:

    1.  **Serving the Frontend:** It serves the static `index.html` file to the user's browser.
    2.  **Securing the API:** The `SecurityConfig` class ensures that only users with a valid JWT from Keycloak can access the `/api/upload` endpoint.
    3.  **Handling Uploads:** The `FileUploadService` takes the file, uploads it to the LocalStack S3 bucket, and sends a `FileProcessMessage` to the LocalStack SQS `pending-queue`. It does this asynchronously (`@Async`) so the user's request returns immediately.
    4.  **Processing Files:** The `SqsListenerService` constantly listens to the `pending-queue`. When a message appears, it:
          * Simulates a "Guarddog" malware scan.
          * Pushes the message to either the `finished-queue` or `malware-queue`.
          * Sends a real-time status update to the user via WebSockets.

  * **Key Concepts:**

      * **Resource Server:** Its security role is to be a "Resource Server," meaning it protects resources (the API) and validates tokens.
      * **Asynchronous Processing:** Using `CompletableFuture` and `@Async` makes the app fast. The user isn't forced to wait for the S3 upload and SQS message to complete.
      * **Message-Driven:** The `SqsListenerService` is a "message-driven microservice." It's idle until a message triggers its logic.

#### 5\. Frontend (`index.html`) (The User Interface)

  * **What it is:** The single HTML file that the user interacts with in their browser.

  * **Role in this App:** It's a surprisingly smart "thin client" that handles all user-facing tasks:

    1.  **Authentication:** Uses the `keycloak.js` library to manage the entire login/logout flow with Keycloak.
    2.  **File Upload:** Uses `Axios` to send the files (as `multipart/form-data`) and the Keycloak JWT to the Spring Boot backend.
    3.  **Real-time Status:** Uses `SockJS` and `STOMP` to open a WebSocket connection to the Spring Boot backend. It subscribes to a *user-specific* topic (e.g., `/topic/status/USER-ID`) and updates the UI in real-time as messages come in (`PENDING`, `PROCESSED`, `MALWARE_DETECTED`).

  * **Key Concepts:**

      * **Single-Page Application (SPA):** Everything happens on one page without full reloads.
      * **Token Handling:** Securely stores the JWT in the browser (managed by `keycloak.js`) and attaches it to API requests.
      * **WebSocket:** Provides a two-way, real-time communication channel between the browser and the server.

-----

### Part 2: The End-to-End Flow

Here is the step-by-step journey of a file upload.

**Flow 1: User Authentication**

1.  A user opens `http://localhost:8080`. The Spring Boot app serves `index.html`.
2.  The `keycloak.js` script in the HTML file runs and sees the user is not logged in.
3.  The user clicks "Login." `keycloak.js` redirects them to the Keycloak server (`http://localhost:8180`).
4.  The user enters their credentials (`user`/`password`) into the Keycloak page.
5.  Keycloak confirms the credentials and redirects the user back to `http://localhost:8080`.
6.  `keycloak.js` (running on the page) detects this, receives the user's JWT, and stores it.
7.  The UI updates to "Logged in as: user" and the upload form appears.
8.  The frontend now opens a WebSocket connection to the backend and subscribes to its unique status topic (e.g., `/topic/status/some-long-user-id`).

**Flow 2: File Upload and Processing**

1.  The user selects two files: `my_document.pdf` and `eicar.txt` (a test malware file).
2.  **Frontend:** The user clicks "Upload." `Axios` sends both files and the JWT to the `/api/upload` endpoint.
3.  **Backend (Security):** Spring Security intercepts the request. It validates the JWT by checking with Keycloak. The token is valid, so the request is allowed.
4.  **Backend (Controller):** The `UploadController` receives the files and the user's ID from the JWT. It loops through the files and calls `fileUploadService.processUpload()` for each one *asynchronously*.
5.  **Backend (Service) - File 1:**
      * `processUpload(my_document.pdf)` is called.
      * The file is uploaded to the **LocalStack S3 bucket**.
      * A message for `my_document.pdf` is sent to the **`pending-queue`** on SQS.
      * A "PENDING" status is sent over **WebSocket** to the user.
6.  **Backend (Service) - File 2:**
      * `processUpload(eicar.txt)` is called.
      * The file is uploaded to the **LocalStack S3 bucket**.
      * A message for `eicar.txt` is sent to the **`pending-queue`** on SQS.
      * A "PENDING" status is sent over **WebSocket** to the user.
7.  **Frontend:** The UI now shows two "PENDING" items in the status list. The API request finishes, and the user can do other things.
8.  **Backend (Listener):** The `SqsListenerService`, which is always listening, detects the messages in `pending-queue`. It processes them one by one.
9.  **Backend (Listener) - File 1:**
      * It processes `my_document.pdf`.
      * The `simulateMalwareScan()` (which includes a 3-second delay) runs.
      * The file is "clean" (`isMalware = false`).
      * The message is sent to the **`finished-queue`**.
      * A "PROCESSED" status is sent over **WebSocket**.
10. **Frontend:** The status for `my_document.pdf` updates to "✅ [PROCESSED]".
11. **Backend (Listener) - File 2:**
      * It processes `eicar.txt`.
      * The `simulateMalwareScan()` runs.
      * The name contains "eicar," so it's "malware" (`isMalware = true`).
      * The message is sent to the **`malware-queue`**.
      * A "MALWARE\_DETECTED" status is sent over **WebSocket**.
12. **Frontend:** The status for `eicar.txt` updates to "☣️ [MALWARE\_DETECTED]".
13. **Flow Complete.**

-----

### Part 3: Tutorial - How to Set Up and Run the App

Follow these steps to get the entire system running on your machine.

**Prerequisites:**

  * Docker & Docker Compose
  * Java (JDK 17+) & Maven
  * All the files you listed, placed in the correct directory structure.

#### Step 1: Make the LocalStack Script Executable

Before you can build the Docker image, you *must* make the `localstack-init.sh` script executable.

```bash
# Navigate to your project's root directory (docker-keycloak-s3-demo)
chmod +x .docker/localstack-init.sh
```

#### Step 2: Configure Keycloak (One-Time Setup)

You must configure Keycloak manually after starting it.

1.  Start *only* Keycloak to set it up:
    ```bash
    docker-compose up -d keycloak
    ```
2.  Wait 30-60 seconds, then open the Keycloak Admin Console: `http://localhost:8180`
3.  Log in with username `admin` and password `admin`.
4.  **Create a Realm:**
      * Hover over the "master" realm name in the top-left and click "Add realm".
      * Enter the **Realm name:** `spring-demo`.
      * Click "Create".
5.  **Create a Client:**
      * In the `spring-demo` realm, click "Clients" in the left-hand menu.
      * Click "Create".
      * **Client ID:** `spring-client`
      * Click "Next".
      * Enable **Client authentication:** `ON`.
      * Click "Next".
      * Under **Valid redirect URIs**, add `http://localhost:8080/*`.
      * Click "Save".
6.  **Create a User:**
      * Click "Users" in the left-hand menu.
      * Click "Add user".
      * **Username:** `user`
      * Click "Create".
      * In the user's "Credentials" tab:
          * Click "Set password".
          * **Password:** `password`
          * **Temporary:** `OFF`
          * Click "Save".

Keycloak is now configured. You can leave it running.

#### Step 3: Run the Entire Application

Now, go back to your terminal in the project's root directory.

1.  Build and run all services (Keycloak, LocalStack, and your Spring app):
    ```bash
    docker-compose up --build
    ```
2.  You will see logs from all three containers. Wait until the `spring-app` log shows "Started DemoApplication".

#### Step 4: Use the Application

1.  Open your browser and go to `http://localhost:8080`.
2.  You'll see "Not logged in." Click "Login".
3.  You'll be sent to the Keycloak page. Log in with `user` / `password`.
4.  You'll be redirected back to the app, which now says "Logged in as: user".
5.  Select any document (a PDF, a text file, an image) and click "Upload".
6.  Watch the "File Status" section. You will see:
      * First, `⏳ [PENDING] Your-File-Name.pdf`
      * After \~3 seconds, `✅ [PROCESSED] Your-File-Name.pdf`

#### Step 5: Test the Malware Scan

1.  Create a new, empty text file on your computer named `eicar.txt`.
2.  In the app, upload `eicar.txt`.
3.  Watch the "File Status" section. You will see:
      * First, `⏳ [PENDING] eicar.txt`
      * After \~3 seconds, `☣️ [MALWARE_DETECTED] eicar.txt`

You have successfully tested the entire asynchronous, secure, message-driven file processing pipeline

- spring-boot-starter-web
- spring-boot-starter-security
- spring-boot-starter-oauth2-resource-server
- spring-boot-starter-websocket
- spring-cloud-aws-starter-sqs
- s3
- lombok
- spring-boot-starter-test

This is a complex, multi-service architecture. I can provide the complete file structure, code, and configuration to build this system.

This solution provides a `docker-compose.yml` to launch **Keycloak** and **LocalStack** (for S3/SQS). It also includes a complete **Spring Boot** application that:

  * Is secured with Keycloak.
  * Serves a static `index.html`.
  * Provides a REST API for file uploads.
  * Uses `CompletableFuture` for asynchronous processing.
  * Uploads files to a LocalStack S3 bucket.
  * Sends messages to a LocalStack SQS `pending-queue`.
  * Uses WebSockets to send real-time status updates to the user.
  * Includes an SQS listener to "process" files (simulating a malware scan) and move them to `finished-queue` or `malware-queue`.

The `index.html` file uses **Tailwind CSS** (via CDN), **Axios**, and the **Keycloak.js** adapter to:

  * Require users to log in via Keycloak.
  * Allow multiple file uploads.
  * Listen for status updates via WebSockets and display them.

-----

### 1\. Project File Structure

Here is the complete file structure for the project.

```
/docker-keycloak-s3-demo
├── .docker/
│   └── localstack-init.sh
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/demo/
│   │   │       ├── DemoApplication.java
│   │   │       ├── config/
│   │   │       │   ├── AwsConfig.java
│   │   │       │   ├── SecurityConfig.java
│   │   │       │   └── WebSocketConfig.java
│   │   │       ├── controller/
│   │   │       │   └── UploadController.java
│   │   │       ├── dto/
│   │   │       │   ├── FileProcessMessage.java
│   │   │       │   └── StatusUpdate.java
│   │   │       └── service/
│   │   │           ├── FileUploadService.java
│   │   │           └── SqsListenerService.java
│   │   └── resources/
│   │       ├── static/
│   │       │   └── index.html
│   │       └── application.properties
├── Dockerfile
├── docker-compose.yml
└── pom.xml
```

-----

### 2\. Docker & Infrastructure

#### `docker-compose.yml`

This file orchestrates our external services (Keycloak, LocalStack) and our Spring Boot app.

```yaml
version: '3.8'

services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    container_name: keycloak
    ports:
      - "8180:8080"
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=admin
    command: "start-dev"
    networks:
      - app-net

  localstack:
    image: localstack/localstack:latest
    container_name: localstack
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,sqs
      - DEFAULT_REGION=us-east-1
      - DEBUG=1
    volumes:
      - ./.docker/localstack-init.sh:/etc/localstack/init/ready.d/init.sh
    networks:
      - app-net

  spring-app:
    build: .
    container_name: spring-app
    ports:
      - "8080:8080"
    depends_on:
      - keycloak
      - localstack
    environment:
      # These URLs use the Docker service names
      - KEYCLOAK_URL=http://keycloak:8080
      - LOCALSTACK_URL=http://localstack:4566
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

#### `.docker/localstack-init.sh`

This script automatically creates our S3 bucket and SQS queues inside LocalStack on startup.

```bash
#!/bin/bash
echo "--- Initializing LocalStack resources ---"

# Make sure to use --endpoint-url and --region
awslocal() {
  aws --endpoint-url=http://localstack:4566 --region=us-east-1 "$@"
}

# Create S3 Bucket
awslocal s3 mb s3://document-bucket
echo "Created S3 bucket: document-bucket"

# Create SQS Queues
awslocal sqs create-queue --queue-name pending-queue
awslocal sqs create-queue --queue-name finished-queue
awslocal sqs create-queue --queue-name malware-queue
echo "Created SQS queues."

echo "--- LocalStack initialization complete ---"
```

**Important:** You must make this script executable: `chmod +x .docker/localstack-init.sh`

-----

### 3\. Spring Boot Application

#### `Dockerfile`

This builds our Spring Boot application into a container.

```dockerfile
# Stage 1: Build the application
FROM maven:3.8-openjdk-17-slim AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# Stage 2: Create the final image
FROM openjdk:17-slim
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

#### `pom.xml`

This file manages all our Java dependencies.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version> <relativePath/>
    </parent>
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo project for Spring Boot</description>

    <properties>
        <java.version>17</java.version>
        <spring-cloud.version>2022.0.4</spring-cloud.version>
        <aws.sdk.version>2.20.43</aws.sdk.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-websocket</artifactId>
        </dependency>
        
        <dependency>
            <groupId>io.awspring.cloud</groupId>
            <artifactId>spring-cloud-aws-starter-sqs</artifactId>
        </dependency>

        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>s3</artifactId>
            <version>${aws.sdk.version}</version>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

#### `src/main/resources/application.properties`

This configures the Spring app, pointing it to Keycloak and LocalStack.

```properties
# Server
server.port=8080

# --- Keycloak Security ---
# This must match the realm you create in Keycloak.
# 'KEYCLOAK_URL' is the env var from docker-compose, defaulting to localhost for local dev
spring.security.oauth2.resourceserver.jwt.issuer-uri=${KEYCLOAK_URL:http://localhost:8180}/realms/spring-demo

# --- AWS LocalStack Configuration ---
# 'LOCALSTACK_URL' is the env var, defaulting for local dev
aws.localstack.endpoint=${LOCALSTACK_URL:http://localhost:4566}

# S3 Client Config (uses aws.localstack.endpoint)
aws.s3.bucket-name=document-bucket

# SQS Listener Config (uses aws.localstack.endpoint)
spring.cloud.aws.region.static=us-east-1
spring.cloud.aws.credentials.access-key=test
spring.cloud.aws.credentials.secret-key=test
spring.cloud.aws.sqs.endpoint=${LOCALSTACK_URL:http://localhost:4566}

# SQS Queue Names (must match localstack-init.sh)
aws.sqs.pending-queue=pending-queue
aws.sqs.finished-queue=finished-queue
aws.sqs.malware-queue=malware-queue
```

#### `src/main/java/com/example/demo/DemoApplication.java`

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@EnableAsync
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

-----

#### Spring Config Files

#### `src/main/java/com/example/demo/config/SecurityConfig.java`

```java
package com.example.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
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
                .anyRequest().permitAll()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable()); // Disable CSRF for this stateless API

        return http.build();
    }
}
```

#### `src/main/java/com/example/demo/config/AwsConfig.java`

We only need to configure the `S3Client`, as Spring Cloud AWS handles the SQS client.

```java
package com.example.demo.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

import java.net.URI;

@Configuration
public class AwsConfig {

    @Value("${aws.localstack.endpoint}")
    private String localstackEndpoint;

    @Bean
    public S3Client s3Client() {
        return S3Client.builder()
                .endpointOverride(URI.create(localstackEndpoint))
                .region(Region.US_EAST_1)
                .credentialsProvider(StaticCredentialsProvider.create(
                        AwsBasicCredentials.create("test", "test"))) // Dummy credentials for LocalStack
                .build();
    }
}
```

#### `src/main/java/com/example/demo/config/WebSocketConfig.java`

```java
package com.example.demo.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        // "/topic" is where clients subscribe to updates
        config.enableSimpleBroker("/topic");
        // "/app" is the prefix for messages sent from client to server (we don't use this here)
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // "/ws" is the endpoint clients connect to
        registry.addEndpoint("/ws").withSockJS();
    }
}
```

-----

#### Spring DTOs (Data Transfer Objects)

#### `src/main/java/com/example/demo/dto/FileProcessMessage.java`

```java
package com.example.demo.dto;

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
```

#### `src/main/java/com/example/demo/dto/StatusUpdate.java`

```java
package com.example.demo.dto;

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
```

-----

#### Spring Services & Controller

#### `src/main/java/com/example/demo/controller/UploadController.java`

```java
package com.example.demo.controller;

import com.example.demo.service.FileUploadService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

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
```

#### `src/main/java/com/example/demo/service/FileUploadService.java`

This service handles the initial upload, S3 push, SQS send, and WebSocket notification.

```java
package com.example.demo.service;

import com.example.demo.dto.FileProcessMessage;
import com.example.demo.dto.StatusUpdate;
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
```

#### `src/main/java/com/example/demo/service/SqsListenerService.java`

This service listens to the `pending-queue`, simulates the "Guarddog" malware scan, and sends results to the other queues.

```java
package com.example.demo.service;

import com.example.demo.dto.FileProcessMessage;
import com.example.demo.dto.StatusUpdate;
import io.awspring.cloud.sqs.annotation.SqsListener;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
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

    @SqsListener(queueNames = "${aws.sqs.pending-queue}", deletionPolicy = SqsListener.DeletionPolicy.ON_SUCCESS)
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
```

-----

### 4\. Frontend

#### `src/main/resources/static/index.html`

This is the single-page frontend.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Document Upload</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sockjs-client@1/dist/sockjs.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@stomp/stompjs@7/bundles/stomp.umd.min.js"></script>
    <script src="http://localhost:8180/js/keycloak.js"></script>
</head>
<body class="bg-gray-100">

    <div class="container mx-auto p-8 max-w-2xl">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Secure Document Upload</h1>

        <div class="bg-white p-4 rounded-lg shadow-md mb-6 flex justify-between items-center">
            <span id="username" class="text-gray-700">Not logged in.</span>
            <div>
                <button id="login-btn" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    Login
                </button>
                <button id="logout-btn" class="hidden bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
                    Logout
                </button>
            </div>
        </div>

        <div id="upload-section" class="hidden bg-white p-6 rounded-lg shadow-md mb-6">
            <h2 class="text-xl font-semibold mb-4">Upload Documents</h2>
            <form id="upload-form">
                <input type="file" id="file-input" multiple
                       class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none" />
                <button type="submit" class="mt-4 w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                    Upload
                </button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-xl font-semibold mb-4">File Status</h2>
            <ul id="status-list" class="list-disc list-inside space-y-2 text-gray-700">
                <li class="text-gray-400">Waiting for uploads...</li>
            </ul>
        </div>
    </div>

    <script>
        // --- Keycloak Configuration ---
        const keycloak = new Keycloak({
            url: "http://localhost:8180",
            realm: "spring-demo",
            clientId: "spring-client"
        });

        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const usernameEl = document.getElementById('username');
        const uploadSection = document.getElementById('upload-section');
        const uploadForm = document.getElementById('upload-form');
        const fileInput = document.getElementById('file-input');
        const statusList = document.getElementById('status-list');
        
        let stompClient = null;

        // --- 1. Keycloak Initialization ---
        keycloak.init({ onLoad: 'check-sso' })
            .then(authenticated => {
                if (authenticated) {
                    console.log('User is authenticated');
                    setupAuthenticatedState(keycloak.tokenParsed);
                    connectWebSocket();
                } else {
                    console.log('User is not authenticated');
                    setupGuestState();
                }
            })
            .catch(err => console.error('Keycloak init failed', err));

        // --- 2. Auth State UI ---
        function setupAuthenticatedState(profile) {
            loginBtn.classList.add('hidden');
            logoutBtn.classList.remove('hidden');
            uploadSection.classList.remove('hidden');
            usernameEl.textContent = `Logged in as: ${profile.preferred_username}`;
            statusList.innerHTML = ''; // Clear "Waiting for uploads"
        }

        function setupGuestState() {
            loginBtn.classList.remove('hidden');
            logoutBtn.classList.add('hidden');
            uploadSection.classList.add('hidden');
            usernameEl.textContent = 'Not logged in.';
            statusList.innerHTML = '<li class="text-gray-400">Please log in to see status.</li>';
        }

        loginBtn.onclick = () => keycloak.login();
        logoutBtn.onclick = () => keycloak.logout();

        // --- 3. WebSocket Connection ---
        function connectWebSocket() {
            if (!keycloak.authenticated) return;

            const socket = new SockJS('/ws');
            stompClient = Stomp.over(socket);

            stompClient.connect({}, (frame) => {
                console.log('Connected to WebSocket: ' + frame);
                // Subscribe to the user-specific topic
                stompClient.subscribe(`/topic/status.${keycloak.subject}`, (message) => {
                    const status = JSON.parse(message.body);
                    console.log('Received status:', status);
                    addStatusItem(status);
                });
            }, (error) => {
                console.error('WebSocket connection error:', error);
                setTimeout(connectWebSocket, 5000); // Try to reconnect
            });
        }

        function addStatusItem(status) {
            const sizeInMB = (status.fileSize / (1024 * 1024)).toFixed(2);
            let statusClass = 'text-blue-500';
            let statusIcon = '⏳';

            if (status.status === 'PROCESSED') {
                statusClass = 'text-green-500';
                statusIcon = '✅';
            } else if (status.status === 'MALWARE_DETECTED') {
                statusClass = 'text-red-500';
                statusIcon = '☣️';
            } else if (status.status === 'ERROR') {
                statusClass = 'text-red-500';
                statusIcon = '❌';
            }

            const li = document.createElement('li');
            li.className = `font-mono ${statusClass}`;
            li.innerHTML = `${statusIcon} [${status.status}] ${status.fileName} (${sizeInMB} MB)`;
            statusList.prepend(li);
        }

        // --- 4. File Upload Handler ---
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!keycloak.authenticated || fileInput.files.length === 0) {
                return;
            }

            try {
                // Ensure token is fresh
                await keycloak.updateToken(30);

                const formData = new FormData();
                for (const file of fileInput.files) {
                    formData.append('files', file);
                }

                // Use Axios to send multipart form data
                const response = await axios.post('/api/upload', formData, {
                    headers: {
                        'Authorization': `Bearer ${keycloak.token}`,
                        'Content-Type': 'multipart/form-data'
                    }
                });

                console.log('Upload successful:', response.data);
                // "PENDING" status will arrive via WebSocket, so no UI update here
                fileInput.value = ''; // Clear the file input

            } catch (error) {
                console.error('Upload failed:', error);
                addStatusItem({
                    status: 'UPLOAD_ERROR',
                    fileName: 'Upload failed, check console',
                    fileSize: 0
                });
            }
        });
    </script>
</body>
</html>
```

-----

### 5\. Required Keycloak Setup

Before running this, you **must** configure Keycloak:

1.  Start Keycloak: `docker-compose up keycloak`
2.  Go to `http://localhost:8180` and log in with `admin` / `admin`.
3.  **Create a Realm:**
      * Hover over "master" and click "Add realm".
      * Set **Realm name** to `spring-demo`. Click "Create".
4.  **Create a Client:**
      * Go to "Clients" and click "Create".
      * Set **Client ID** to `spring-client`.
      * Click "Next".
      * Enable **Client authentication** (set it to ON).
      * Click "Next".
      * In **Valid redirect URIs**, add `http://localhost:8080/*` (for the Spring Boot app).
      * Click "Save".
5.  **Create a User:**
      * Go to "Users" and click "Add user".
      * Set **Username** (e.g., `user`) and click "Create".
      * Go to the "Credentials" tab, set a password (e.g., `password`), and turn **Temporary** OFF.

### 6\. How to Run

1.  Make the LocalStack script executable: `chmod +x .docker/localstack-init.sh`
2.  Build and run all services: `docker-compose up --build`
3.  Wait for all services to start.
4.  Open `http://localhost:8080` in your browser.
5.  Click "Login". You will be redirected to the Keycloak page.
6.  Log in with `user` / `password`.
7.  You will be redirected back, and the upload form will appear.
8.  Select one or more files and click "Upload".
9.  Watch the "File Status" section update in real-time as the files are processed, "scanned", and finished.

