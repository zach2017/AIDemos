# Stage 1: Build the frontend (if applicable)
FROM node:18 AS builder
WORKDIR /app
COPY frontend /app
RUN mkdir -p /frontend_dist && cp -r /app/* /frontend_dist/

# Stage 2: Build the backend
FROM golang:1.21 AS backend
WORKDIR /app
COPY . /app
RUN go mod tidy && go build -o /app


# Expose port 80 for frontend
EXPOSE 8081

