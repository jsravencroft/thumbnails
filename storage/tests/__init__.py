import os

os.environ['AWS_DEFAULT_REGION']    = "local"
os.environ['AWS_ACCESS_KEY_ID']     = "test_access"
os.environ['AWS_SECRET_ACCESS_KEY'] = "test_secret"
os.environ['S3_ENDPOINT']           = "http://localhost:9000"
os.environ['S3_BUCKET']             = "testing"
os.environ['SQS_ENDPOINT']          = "http://localhost:9324"
os.environ['SQS_QUEUE']             = "testing"
os.environ['SQS_QUEUE_URL']         = "http://localhost:9324/queue/testing"

print("%s" % os.environ)
