from PIL import Image
from io import BytesIO
import boto3
import urllib.parse
from datetime import datetime

s3 = boto3.client('s3')

# NEW
sqs = boto3.client('sqs')

# NEW
sns = boto3.client('sns')

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('SmartSnapTable')

BUCKET_NAME = "smartsnap-project-demo"

# NEW
QUEUE_URL = "https://sqs.ap-south-1.amazonaws.com/733050719092/SmartSnapQueue"

# NEW
TOPIC_ARN = "arn:aws:sns:ap-south-1:733050719092:SmartSnapNotification"

def lambda_handler(event, context):

    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key']
    )

    print(f"Uploaded File: {key}")
    
    # Process only input folder
    if not key.startswith("input/"):

        print("Not input folder")

        return

    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=key
    )

    print("Downloaded from S3")

    image_content = response['Body'].read()

    print("Image bytes read")

    image = Image.open(BytesIO(image_content))

    print(f"Original size: {image.size}")

    resized_image = image.resize((300,300))

    print("Resize completed")

    buffer = BytesIO()

    resized_image.save(
        buffer,
        format=image.format
    )

    print("Saved to buffer")

    output_key = f"output/resized-{key.split('/')[-1]}"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=output_key,
        Body=buffer.getvalue()
    )

    print(f"Uploaded: {output_key}")

    # -----------------------------------
    # STORE METADATA IN DYNAMODB
    # -----------------------------------

    table.put_item(

        Item={

            'image_name': key.split('/')[-1],

            'original_path': key,

            'resized_path': output_key,

            'timestamp': str(datetime.now())
        }
    )

    print("Metadata stored in DynamoDB")

    # -----------------------------------
    # SEND MESSAGE TO SQS
    # -----------------------------------

    sqs.send_message(
        QueueUrl=QUEUE_URL,

        MessageBody=f"""
Image processed successfully

Original File: {key}

Resized File: {output_key}
"""
    )

    print("Message sent to SQS")

    # -----------------------------------
    # SEND SNS EMAIL
    # -----------------------------------

    sns.publish(

        TopicArn=TOPIC_ARN,

        Subject="SmartSnap Notification",

        Message=f"""
Image Processed Successfully

Original File:
{key}

Resized File:
{output_key}
"""
    )

    print("SNS notification sent successfully")

    return {
        "statusCode": 200
    }
