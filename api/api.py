import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from   datetime import datetime
from   flask import Flask, request, jsonify, send_file
from   io import BytesIO
import os
from   PIL import Image
import uuid
import storage
from   waitress import serve

app = Flask(__name__)

#POST   /jobs
@app.route('/jobs', methods=['POST'])
def post_job():
  # TODO - Permissions
  new_job = {
    'id':     str(uuid.uuid4()),
    'status': "pending",
    'start':  datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
  }

  try:
    image = Image.open(request.files['image'])
    if logging.getLogger().level == logging.DEBUG:
      image.show()
    storage.write_s3_image(new_job, image, "input")
    storage.write_s3_job(new_job)
    storage.write_sqs_job(new_job)
    new_job['code']     = 202

  except Exception as e:
    new_job['status']  = "failed"
    new_job['message'] = str(e)
    new_job['location'] = "jobs/%s" % new_job['id']
    new_job['code']    = 500
    storage.write_s3_job(new_job)

  new_job['location'] = "jobs/%s" % new_job['id']

  response = jsonify(new_job)
  response.location  = new_job['location']
  response.status_code = new_job['code']

  logging.info("%s" % response)
  return response, new_job['code']

#GET    /jobs/{job_id}
@app.route('/jobs/<string:job_id>')
def get_job(job_id):
  # TODO - Permissions
  job_status = {
    'id': job_id,
  }
  try:
    job_status = storage.read_s3_job(job={ 'id': job_id })

    if job_status['status'] == "pending":
      job_status['code'] = 200

    elif job_status['status'] == "processing":
      job_status['code'] = 200

    elif job_status['status'] == "failed":
      job_status['code'] = 200

    elif job_status['status'] == "complete":
      job_status['location'] = "jobs/%s/output" % job_status['id']
      job_status['code'] = 201

    else:
      job_status['code'] = 500

    logging.info("%s" % job_status)
    return jsonify(job_status), job_status['code']

  except storage.NoSuchKey as nsk:
    job_status['message'] = "No such job"
    job_status['code']    = 404
  except Exception as e:
    job_status['message'] = str(e)
    logging.error("Get Job Output Exception: %s" % job_status['message'])
    job_status['code']    = 500

  return jsonify(job_status), job_status['code']

@app.route('/jobs/<string:job_id>/output')
def get_job_output(job_id):
  # TODO - Permissions
  try:
    image = storage.read_s3_image(job={ 'id': job_id }, target="output")
    output_bytes = BytesIO()
    image.save(output_bytes, 'JPEG') 
    output_bytes.seek(0)
    return send_file(
      output_bytes,
      attachment_filename="%s.jpeg" % job_id,
      mimetype="image/jpeg",
    )

  except storage.NoSuchKey as nsk:
    job_status = {
      'id':      job_id,
      'message': "No such file",
      'code':    404,
    }
    return jsonify(job_status), job_status['code']

  except Exception as e:
    job_status = {
      'id':      job_id,
      'message': str(e),
      'code':    404,
    }
    logging.error("Get Job Output Exception: %s" % job_status['message'])
    return jsonify(job_status), job_status['code']
