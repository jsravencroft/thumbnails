import boto3
from   datetime import datetime
from   io import BytesIO
import json
import logging
import os
from   PIL import Image

s3_client  = boto3.client(service_name='s3', endpoint_url=os.getenv('S3_ENDPOINT'))
sqs_client = boto3.client(service_name='sqs', endpoint_url=os.getenv('SQS_ENDPOINT'))

s3_job_key = "jobs/%s.json"
s3_input_key  = "input/%s.jpg"   # TODO - Multiple content types
s3_output_key = "output/%s.jpg"  # TODO - Multiple content types

# Local Exceptions
class NoSuchKey(Exception):
  pass

# Check SQS Queue Exists, Make if It Doesn't
def setup_storage():
  # Check for QUEUE
  try:
   if os.getenv('SQS_QUEUE_URL') not in sqs_client.list_queues()['QueueUrls']:
    logging.info("Creating SQS Queue: %s" % os.getenv('SQS_QUEUE'))
    sqs_client.create_queue(QueueName=os.getenv('SQS_QUEUE'))
  except Exception as e:
    logging.error("Storage Setup Queue Error: %s" % str(e))

  try:
    buckets = s3_client.list_buckets()['Buckets']
    bucket_names = []
    for b in buckets:
      bucket_names.append(b['Name'])
    if os.getenv('S3_BUCKET') not in bucket_names:
      logging.info("Creating S3 Bucket: %s" % os.getenv('S3_BUCKET'))
      s3_client.create_bucket(Bucket=os.getenv('S3_BUCKET'))
  except Exception as e:
    logging.error("Storage Setup Bucket Error: %s" % str(e))

# SQS Messages Contain Only the Job Id from the Job
def write_sqs_job(job: dict) -> None:
  try:
    sqs_client.send_message(
      QueueUrl=os.getenv('SQS_QUEUE_URL'),
      MessageBody = json.dumps({ 'id': job['id'] }),
    )
  except Exception as e:
    logging.error("Write SQS Job Exception: %s" % str(e))
    raise e

# Returns a Job (dict) Message Receipt -or- None & None
def read_sqs_job() -> dict:
  try:
    response = sqs_client.receive_message(
      QueueUrl          = os.getenv('SQS_QUEUE_URL'),
      WaitTimeSeconds   = 20,
      VisibilityTimeout = 60,
    )
    if "Messages" in response:
      return json.loads(response['Messages'][0]['Body']), response['Messages'][0]['ReceiptHandle']
    else:
     return None, None
  except Exception as e:
    logging.error("Read SQS Job Exception: %s" % str(e))
    return None, None

def delete_sqs_job(receiptHandle: str) -> None:
  try:
    sqs_client.delete_message(
      QueueUrl          = os.getenv('SQS_QUEUE_URL'),
      ReceiptHandle     = receiptHandle,
    )
  except Exception as e:
    logging.error("Delete SQS Job Exception: %s" % str(e))
    raise e
      
# S3
def write_s3_job(job: dict):
  try:
    s3_client.put_object(
      Bucket = os.getenv('S3_BUCKET'),
      Key    = s3_job_key % job['id'],
      Body   = json.dumps(job),
    )
  except Exception as e:
    logging.error("Write S3 Job Exception: %s" % str(e))
    raise e

def read_s3_job(job: dict) -> dict:
  try:
    response = s3_client.get_object(
      Bucket = os.getenv('S3_BUCKET'),
      Key    = s3_job_key % job['id'],
    )
    job = json.loads(response['Body'].read().decode('utf-8'))
    return job
  except s3_client.exceptions.NoSuchKey as nsk:
    raise NoSuchKey()
  except Exception as e:
    logging.error("Read S3 Job Exception: %s" % str(e))
    raise e
  
def write_s3_image(job: dict, image: Image, target: str):
  targets = { "input", "output" }
  if target not in targets:
    raise Exception("Write S3 Image target must be in %s" % targets)

  s3_key = ""
  if target == "input":
    s3_key = s3_input_key % job['id']
  else:
    s3_key = s3_output_key % job['id']
    
  try:
    output_bytes = BytesIO()
    image.save(output_bytes, 'JPEG')
    output_bytes.seek(0)
    s3_client.put_object(
      Bucket = os.getenv('S3_BUCKET'),
      Key    = s3_key,
      Body   = output_bytes.read(),
    )
  except Exception as e:
    logging.error("Read S3 Job Exception: %s" % str(e))
    raise e
  
def read_s3_image(job: dict, target: str) -> Image:
  targets = { "input", "output" }
  if target not in targets:
    raise Exception("Write S3 Image target must be in %s" % targets)

  s3_key = ""
  if target == "input":
    s3_key = s3_input_key % job['id']
  else:
    s3_key = s3_output_key % job['id']

  try:
    response = s3_client.get_object(
      Bucket = os.getenv('S3_BUCKET'),
      Key    = s3_key,
    )
    image = Image.open(BytesIO(response['Body'].read()))
    return image
  except s3_client.exceptions.NoSuchKey as nsk:
    raise NoSuchKey()
  except Exception as e:
    logging.error("Read S3 Job Exception: %s" % str(e))
    raise e
