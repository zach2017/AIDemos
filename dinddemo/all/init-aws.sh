#!/bin/bash

echo "Initializing AWS LocalStack resources..."

# Wait for LocalStack to be ready
until curl -s http://localhost:4566/_localstack/health | grep -q '"s3":"available"'; do
    echo "Waiting for LocalStack..."
    sleep 5
done

# Create S3 bucket
aws --endpoint-url=http://localhost:4566 \
    --region=us-east-1 \
    s3 mb s3://test-bucket

echo "S3 bucket 'test-bucket' created"

# Create SQS queue
aws --endpoint-url=http://localhost:4566 \
    --region=us-east-1 \
    sqs create-queue --queue-name test-queue

echo "SQS queue 'test-queue' created"

# List resources
echo "Created resources:"
aws --endpoint-url=http://localhost:4566 --region=us-east-1 s3 ls
aws --endpoint-url=http://localhost:4566 --region=us-east-1 sqs list-queues

echo "AWS resources initialized successfully"
