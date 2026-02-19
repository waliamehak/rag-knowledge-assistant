import boto3
import json
import os

sqs = boto3.client("sqs", region_name="us-east-1")
QUEUE_URL = os.getenv("SQS_QUEUE_URL")


def enqueue_document(job_id, s3_key, filename):
    # Push a processing job onto the queue — worker Lambda picks it up asynchronously
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({
            "job_id": job_id,
            "s3_key": s3_key,
            "filename": filename,
        }),
    )
