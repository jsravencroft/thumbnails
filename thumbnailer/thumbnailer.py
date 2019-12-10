import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from   datetime import datetime
import PIL
from   PIL import Image
import storage

class Thumbnailer:

  def __init__(self, Polling=False):
    if Polling is True:
      self._polling = True
      self.start_polling()

  #Start Polling SQS
  def start_polling(self):
    logging.info("Starting Thumbnailer Poll")
    self._polling = True
    while self._polling:
      self.operational_loop()
      if self._polling == False:
        break

  # This is a full loop: Read SQS Job, Read S3 Job, Read Source Image, Make Thumbnail, Write Thumbnail, Write Job Result
  def operational_loop(self):
    logging.info("Thumbnailer::operational_loop starting")
    

    # Read SQS Job & Receipt Handler, Poll Again if No Job
    job, receipt = storage.read_sqs_job()
    if job == None:
      return 

    # Read S3 Job
    try:
      s3_job = storage.read_s3_job({ 'id': job['id'] })
      if s3_job['status'] != 'pending':
        logging.info("Thumbnailer::operational_loop: non-pending job received: %s" % job['id'])
        return
    except storage.NoSuchKey:
      logging.error("Thumbnailer::operational_loop: no such key from S3 job: %s" % job['id'])
      storage.delete_sqs_job(receipt)  # Delete the SQS Message
      retun
    except Exception as e:
      logging.error("Thumbnailer::operational_loop: exception: %s" % str(e))
      return

    # Read S3 Source Image
    try:
      s3_image= storage.read_s3_image( job=s3_job, target="input")
    except storage.NoSuchKey:
      logging.error("Thumbnailer::operational_loop: no such key from S3 job: %s" % job['id'])
      s3_job['message'] = "No corresponding image found"
      s3_job['status']  = "failed"
      s3_job['finish']  = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
      storage.write_s3_job(s3_job)
      storage.delete_sqs_job(receipt)  # Delete the SQS Message
      return
    except Exception as e:
      logging.error("Thumbnailer::operational_loop: exception: %s" % str(e))
      return

    # Make Thumbnail
    try:
      thumbnail_image = self.make_thumbnail(s3_image)
    except Exception as e:
      logging.error("Thumbnailer::operational_loop: exception: %s" % str(e))
      return

    # Write Thumbnail
    try:
      storage.write_s3_image(job=s3_job, image=thumbnail_image, target="output")
    except:
      logging.error("Thumbnailer::operational_loop: exception: %s" % str(e))
      return

    # Write S3 Job
    s3_job['status'] = "complete"
    s3_job['finish']  = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    storage.write_s3_job(s3_job)
    storage.delete_sqs_job(receipt)  # Delete the SQS Message

    # Delete SQS Message
    storage.delete_sqs_job(receipt)  # Delete the SQS Message

  def make_thumbnail(self, image: Image, ThumbnailSize=((100, 100))) -> Image:
    try:
      # Crop the image into a square
      if image.size[0] > image.size[1]:
        trim = (image.size[0] - image.size[1])/2
        image = image.crop( (trim, 0, image.size[0] - trim, image.size[1]))
      if image.size[1] > image.size[0]:
        trim = (image.size[0] - image.size[1])/2
        image = image.crop( (0, trim, image.size[1], image.size[0] - trim))
      image.thumbnail(ThumbnailSize)
      return image
    except Exception as e:
      logging.error("Exception in Thumbnailer::make_thumbnail: %s" % str(e))
      raise e
