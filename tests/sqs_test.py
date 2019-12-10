import boto3

from datetime import datetime

class TestSQS:

  def test_sqs(self):
    _time       = datetime.now().strftime("%Y%m%d%H%M%S")  # String format of time for uniqueness of test
    _endpoint   = "http://localhost:9324"
    _queue_name = "test" + _time
    _queue_url  = _endpoint + "/queue/" + _queue_name     # Standard queue URL is http(s)://hostname:port/queues/queue_name
    _message    = "This is a test message for test run at " + _time

    _sqs_client = boto3.client(service_name='sqs', endpoint_url=_endpoint) 

    # CREATE QUEUE
    _sqs_client.create_queue(QueueName=_queue_name)

    # VERIFY QUEUE (CHANGE TO https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.get_queue_url)
    queues = _sqs_client.list_queues()
    print("Queues: " + str(queues))
    assert _queue_url in queues['QueueUrls']

    # POST MESSAGE
    send_response = _sqs_client.send_message(
      QueueUrl    = _queue_url,
      MessageBody = _message
    )
    print("Send Response: " + str(send_response))

    # RECEIVE MESSAGE
    read_response = _sqs_client.receive_message(
      QueueUrl    = _queue_url,
    )
    print("Read Response: " + str(read_response))
    assert len(read_response['Messages']) == 1

    # COMPARE MESSAGE
    assert read_response['Messages'][0]['MessageId'] == send_response['MessageId']
  
    # DELETE MESSAGE
    _sqs_client.delete_message(
        QueueUrl      = _queue_url,
        ReceiptHandle = read_response['Messages'][0]['ReceiptHandle'],
    )

    # RECEIVE MESSAGE, SHOULD BE NO MESSAGE & NO 'Messages' KEY
    read_response = _sqs_client.receive_message(
      QueueUrl    = _queue_url,
    )
    print("Read Response: " + str(read_response))
    assert read_response.get('Message') == None

    # DELETE TOPIC
    _sqs_client.delete_queue(
      QueueUrl = _queue_url,
    )

    # VERIFY QUEUE DELETION
    queues = _sqs_client.list_queues()
    print("Queues: " + str(queues))
    assert _queue_url not in queues['QueueUrls']
