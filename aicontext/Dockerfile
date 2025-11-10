# Stage 1: Build the application with Maven and JDK 21
# We use an official Maven image that is based on Eclipse Temurin (JDK) 21 and Alpine
FROM maven:3.9-eclipse-temurin-21-alpine AS build
WORKDIR /app

# Copy pom.xml first to leverage Docker layer caching
# Dependencies will only be re-downloaded if pom.xml changes
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy the rest of your source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Stage 2: Create the final image with JRE 21
# We use a minimal JRE 21 image, also based on Alpine
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Copy the built .jar file from the 'build' stage
COPY --from=build /app/target/*.jar app.jar

# Define the command to run your application
ENTRYPOINT ["java", "-jar", "app.jar"]