import json
import os
from dotenv import load_dotenv
from document_processor import extract_text_from_pdf, chunk_text
from pinecone_handler import store_chunks
from s3_handler import download_from_s3
from db_handler import update_job

load_dotenv()


def handler(event, context):
    # Lambda entry point — SQS triggers this with a batch of records
    failed = []

    for record in event["Records"]:
        body = json.loads(record["body"])
        job_id = body["job_id"]
        s3_key = body["s3_key"]
        filename = body["filename"]

        local_path = f"/tmp/{job_id}.pdf"

        try:
            update_job(job_id, status="processing")

            success = download_from_s3(s3_key, local_path)
            if not success:
                raise Exception("S3 download failed")

            text = extract_text_from_pdf(local_path)
            chunks = chunk_text(text)

            # Embeds all chunks in batches and upserts into Pinecone
            chunks_created = store_chunks(chunks, filename)

            update_job(job_id, status="completed", chunks_created=chunks_created)

        except Exception as e:
            update_job(job_id, status="failed", error=str(e))
            # Report only this message as failed — SQS retries it without reprocessing the rest of the batch
            failed.append({"itemIdentifier": record["messageId"]})

        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    return {"batchItemFailures": failed}
