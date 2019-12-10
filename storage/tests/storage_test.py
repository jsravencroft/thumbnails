import os
from PIL     import Image
from storage import storage

class TestStorage:

  def test_sqs(self):
    # Create Message
    write_job = { 'id': 'test_job', 'status': 'PENDING' }
    storage.write_sqs_job(write_job)

    # Read Message
    read_job, read_receipt = storage.read_sqs_job()

    assert write_job['id'] == read_job['id']

    # Delete Message
    storage.delete_sqs_message(read_receipt)

  def test_s3_job(self):
    test_job = { 'id': 'test_job', 'status': 'PENDING' }

    # WRITE JOB
    write_response = storage.write_s3_job(test_job)

    # RECEIVE ITEM
    read_job = storage.read_s3_job(test_job)
    print("Read Response: " + str(read_job))

    # COMPARE ITEM
    assert test_job == read_job

  def test_s3_image(self):
    # OPEN IMAGE
    write_image = Image.open(os.path.join(os.path.dirname(__file__), 'rainier.jpg'))
    write_job = { 'id': "imageJob" }

    # WRITE IMAGE
    storage.write_s3_image(job=write_job, image=write_image, target="input")

    # READ IMAGE
    read_image = storage.read_s3_image(job=write_job, target="input")

    write_image.show()
    read_image.show()
    
    
