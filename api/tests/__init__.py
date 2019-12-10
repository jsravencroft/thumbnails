from  datetime import datetime
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

os.environ['AWS_ACCESS_KEY_ID']     = os.getenv('AWS_ACCESS_KEY_ID')     if  os.getenv('AWS_ACCESS_KEY_ID')     is not None else "test_access"
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY') if  os.getenv('AWS_SECRET_ACCESS_KEY') is not None else "test_secret"
os.environ['SQS_ENDPOINT']          = os.getenv('SQS_ENDPOINT')          if  os.getenv('SQS_ENDPOINT')          is not None else "http://localhost:9324" # Local ElasticMQ
os.environ['SQS_QUEUE']             = os.getenv('SQS_QUEUE')             if  os.getenv('SQS_QUEUE')             is not None else "test_queue"            # TODO - Dynamic
os.environ['SQS_QUEUE_URL']         = os.getenv('SQS_ENDPOINT') + "/queue/" + os.getenv('SQS_QUEUE')
os.environ['S3_ENDPOINT']           = os.getenv('S3_ENDPOINT')           if  os.getenv('S3_ENDPOINT')           is not None else "http://localhost:9000" # Local Minio
os.environ['S3_BUCKET']             = os.getenv('S3_BUCKET')             if  os.getenv('S3_BUCKET')             is not None else "test" + datetime.now().strftime("%Y%m%d%H%M%S")

from storage import storage
storage.setup_storage()
