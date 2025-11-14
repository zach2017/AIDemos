#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Waiting for LocalStack to be ready..."
# A simple wait loop. In production, you'd use a tool like wait-for-it.
until curl -s "${AWS_ENDPOINT_URL}/_localstack/health" | grep '"services":' | grep '"running"' > /dev/null; do
  sleep 2
  echo -n "."
done
echo "LocalStack is ready!"

echo "Configuring AWS resources..."

# 1. Create S3 Bucket
echo "Creating S3 bucket: my-document-bucket"
awslocal s3api create-bucket --bucket my-document-bucket --region us-east-1

# 2. Create SQS Queue
echo "Creating SQS queue: document-queue"
QUEUE_URL=$(awslocal sqs create-queue --queue-name document-queue --query 'QueueUrl' --output text)
echo "Created SQS Queue: $QUEUE_URL"

# 3. Create Lambda Function
echo "Creating Lambda function zip..."
# 'apk add' is for the amazon/aws-cli (alpine) image
apk add zip > /dev/null
cd /lambda_code
zip /tmp/upload-lambda.zip app.py
cd /

echo "Creating Lambda function: upload-lambda"
LAMBDA_ARN=$(awslocal lambda create-function \
    --function-name upload-lambda \
    --runtime python3.9 \
    --handler app.handler \
    --memory-size 128 \
    --zip-file fileb:///tmp/upload-lambda.zip \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment "Variables={S3_BUCKET=my-document-bucket,SQS_QUEUE_URL=$QUEUE_URL}" \
    --query 'FunctionArn' --output text)
echo "Created Lambda: $LAMBDA_ARN"

# 4. Create API Gateway
echo "Creating API Gateway: DocumentUploadAPI"
API_ID=$(awslocal apigateway create-rest-api --name 'DocumentUploadAPI' --query 'id' --output text)
PARENT_ID=$(awslocal apigateway get-resources --rest-api-id $API_ID --query 'items[0].id' --output text)
RESOURCE_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $PARENT_ID --path-part 'upload' --query 'id' --output text)

# 5. Create POST method and enable CORS
echo "Configuring API Gateway POST method..."
awslocal apigateway put-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --authorization-type NONE

# Add an OPTIONS method for CORS preflight requests
awslocal apigateway put-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --authorization-type NONE
awslocal apigateway put-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 \
    --response-parameters "method.response.header.Access-Control-Allow-Headers=true,method.response.header.Access-Control-Allow-Methods=true,method.response.header.Access-Control-Allow-Origin=true" \
    --response-models "{\"application/json\": \"Empty\"}"
awslocal apigateway put-integration --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --type MOCK \
    --request-templates "{\"application/json\": \"{\\\"statusCode\\\": 200}\"}" \
    --integration-response "{\"statusCode\": \"200\", \"responseParameters\": {\"method.response.header.Access-Control-Allow-Headers\": \"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'\", \"method.response.header.Access-Control-Allow-Methods\": \"'POST,OPTIONS'\", \"method.response.header.Access-Control-Allow-Origin\": \"'*'\"}}"

# 6. Integrate API Gateway with Lambda
echo "Integrating API Gateway with Lambda..."
LAMBDA_URI="arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"
awslocal apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri $LAMBDA_URI \
    --passthrough-behavior WHEN_NO_MATCH

# 7. Deploy API
echo "Deploying API Gateway..."
awslocal apigateway create-deployment --rest-api-id $API_ID --stage-name dev

# 8. Add Lambda permissions for API Gateway to invoke it
awslocal lambda add-permission \
    --function-name $LAMBDA_ARN \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:000000000000:$API_ID/*/POST/upload"

FINAL_URL="http://localhost:4566/restapis/$API_ID/dev/upload"

echo "------------------------------------------------------------------"
echo "✅ AWS Resources Configured!"
echo ""
echo "Frontend is available at: http://localhost:8080"
echo ""
echo "!!!!!!!!!!!!!!!!!!!!!!!!!! ACTION REQUIRED !!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "You MUST copy the URL below and paste it into the"
echo "'API_ENDPOINT' variable in your 'frontend/index.html' file:"
echo ""
echo "$FINAL_URL"
echo ""
echo "After updating the file, refresh your browser to use the app."
echo "------------------------------------------------------------------"