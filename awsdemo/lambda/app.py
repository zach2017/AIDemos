import json
import boto3
import base64
import os
import sys

# Get environment variables set by the init script
S3_BUCKET = os.environ.get('S3_BUCKET')
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

# Use endpoint_url to target LocalStack
# In a real AWS env, you would not pass endpoint_url
ENDPOINT_URL = "http://localstack:4566"

# Check if we are in the LocalStack environment
if os.environ.get('AWS_EXECUTION_ENV') == 'AWS_Lambda_python3.9':
    # Inside the Lambda runtime, boto3 is pre-installed
    # We must use the service name 'localstack' as the host
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_URL)
    sqs = boto3.client('sqs', endpoint_url=ENDPOINT_URL)
else:
    # For local testing (if ever needed)
    s3 = boto3.client('s3')
    sqs = boto3.client('sqs')


def handler(event, context):
    """
    Lambda function triggered by API Gateway.
    Expects a JSON body with:
    {
        "file_name": "example.txt",
        "file_data": "BASE64_ENCODED_STRING",
        "metadata": "{'key': 'value'}"
    }
    """
    try:
        # API Gateway proxy integration wraps the body in a string
        if isinstance(event.get('body'), str):
            body = json.loads(event.get('body', '{}'))
        else:
            body = event.get('body', {})

        file_name = body.get('file_name')
        file_data_b64 = body.get('file_data')
        metadata_str = body.get('metadata', '{}')

        if not file_name or not file_data_b64:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing file_name or file_data'})
            }

        # 1. Decode and Upload to S3
        file_content = base64.b64decode(file_data_b64)
        
        s3_response = s3.put_object(
            Bucket=S3_BUCKET,
            Key=file_name,
            Body=file_content
        )
        
        # Use ETag as a unique-ish ID for this example
        file_id = s3_response.get('ETag', 'unknown-id').strip('"')

        # 2. Publish event to SQS
        sqs_message = {
            'document_id': file_id,
            'file_name': file_name,
            's3_bucket': S3_BUCKET,
            'metadata': metadata_str, # Pass metadata string as-is
            'status': 'upload_complete'
        }
        
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(sqs_message)
        )

        # 3. Return success response to the HTML page
        return {
            'statusCode': 200,
            # IMPORTANT: Add CORS headers for the browser
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': f'File {file_name} uploaded successfully',
                'document_id': file_id
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }