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