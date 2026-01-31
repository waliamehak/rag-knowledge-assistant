import boto3
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client('s3')
BUCKET_NAME = "rag-documents-mehak-2026"

def upload_to_s3(local_file_path, s3_key):
    # Upload file to S3
    try:
        s3_client.upload_file(local_file_path, BUCKET_NAME, s3_key)
        return True
    except Exception as e:
        print(f"S3 upload error: {e}")
        return False

def download_from_s3(s3_key, local_file_path):
    # Download file from S3
    try:
        s3_client.download_file(BUCKET_NAME, s3_key, local_file_path)
        return True
    except Exception as e:
        print(f"S3 download error: {e}")
        return False