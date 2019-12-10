import boto3
import pytest

from datetime import datetime

class TestS3:

  def test_s3(self):
    _access_key  = 'test_access'
    _secret_key  = 'test_secret'
    _endpoint    = "http://localhost:9000"
    _s3_client   = boto3.client(service_name='s3', endpoint_url=_endpoint, aws_access_key_id=_access_key, aws_secret_access_key=_secret_key) 

    _time         = datetime.now().strftime("%Y%m%d%H%M%S")  # String format of time for uniqueness of test
    _bucket_name  = "test" + _time
    _key          = "testObject"
    _write_object = "This is a test message for test run at " + _time

    # CREATE BUCKET
    _s3_client.create_bucket(Bucket=_bucket_name)

    # VERIFY BUCKET
    _buckets      = _s3_client.list_buckets()['Buckets']
    _bucket_names = []
    for b in _buckets:
      _bucket_names.append(b['Name'])
    assert _bucket_name in _bucket_names

    # WRITE ITEM
    _write_response = _s3_client.put_object(
      Bucket = _bucket_name,
      Key    = _key,
      Body   = _write_object,
    )

    # RECEIVE ITEM
    _read_response = _s3_client.get_object(
      Bucket = _bucket_name,
      Key    = _key,
    )
    _read_object = _read_response['Body'].read().decode('utf-8') 
    print("Read Response: " + _read_object)

    # COMPARE ITEM
    assert _write_object == _read_object
  
    # DELETE ITEM
    _s3_client.delete_object(
      Bucket = _bucket_name,
      Key    = _key,
    )

    # RECEIVE ITEM (SHOULD RAISE EXCEPTION)
    with pytest.raises(Exception):
      _s3_client.get_object(
       Bucket = _bucket_name,
       Key    = _key,
      )

    # DELETE BUCKET
    _s3_client.delete_bucket(
      Bucket = _bucket_name,
    )

    # VERIFY BUCKET DELETION
    _buckets      = _s3_client.list_buckets()['Buckets']
    _bucket_names = []
    for b in _buckets:
      _bucket_names.append(b['Name'])
    assert _bucket_name not in _bucket_names
