# SmartSnap

## AWS Services Used
- Amazon S3
- AWS Lambda
- Amazon DynamoDB
- Amazon SQS
- Amazon SNS

## Project Flow

User uploads image
      ↓
S3 stores image
      ↓
Lambda automatically triggers
      ↓
Lambda resizes image
      ↓
DynamoDB stores metadata
      ↓
SQS handles queue
      ↓
SNS sends notification

## CI/CD
Whenever lambda_function.py is updated in GitHub, GitHub Actions automatically deploys the latest code to AWS Lambda.
