# Introduction

This is the web module.  It provides three basic API requests, in order-of-usage:

## API CALLS

### POST an Image to /jobs
  1. The user posts an image to this URL, for example: `curl -X POST -F "image=@tests/rainier.jpg" http://localhost:5000/jobs`
  * If accepted:
    1. a job identified by UUID is created 
    2. if logging is set to Debug, the image will be shown with PIL::Imag.eshow()
    3. an SQS message is created in the queue at the value of environment variable SQS_QUEUE_URL
    4. an S3 job object is created at /jobs/{job_id} 
    5. an S3 image object is created at /input/{job_id}
    6. user is given a response having:
      * status code of 202 (Accepted)
      * a location header and body key identifying the location of job status information
  * If not accepted:
    1. a job identified by UUID is created 
    2. an S3 job object is created at /jobs/{job_id} 
    3. create a response having:
      * status code of 500 (Internal Server Error)
      * a location header and body key identifying the location of job status information
  2. The job status is returned to the user

### GET Job Status from /jobs/{job_id}
  1. The user submits a GET request with a job UUID in the path at {job_id}
    1. The job information is read from the job information DB (currently S3)
      * If the job is pending, processing, or failed:
        * status code of 200 (OK)
      * If the job is completed:
        * status code of 201 (Created)
        * a location header and body key identifying the location of job output
      * If no job status is found:
        * status code of 404 (Not Found)
      * If the information is unknown:
        * status code of 500 (Internal Server Error)
        * possible error written to job['message']
  2. The job status is returned to the user

*A failed job returns a 200 because the request is for the status of the job*

### GET Job Output from /jobs/{job_id}/output
  1 The user submits a GET request with a job UUID in the path at {job_id}
    1. The job output is read from object storage (current S3)
      * If the image is read correctly:
        1. User is returned the image        
      * If the image is not found:
        1. User is returned a 404 message in JSON format
      * Any other result:
        1. The user is returned a 500 message

## Issues
* System-wide issues are listed in the system-wide README*

* Usage is anonymous making it unbillable
* Service is dependent on availability of SQS and S3 or compatible, it's not easily portable
* Possibly crashable with very large files
* /jobs/{job_id}/output should return a location of the if the job is pending or processing
* When storage starts, it attempts to create SQS queues by matching the queue URL

## Opportunities / Roadmap (In Order of Priority)

*System-wide opportunities are listed in the system-wide README*

*This list is based on customer and business needs first, followed by operational enhancements, then convenience features.*

1. Authentiate users using an Authorization header or other token-bearing header
1. Authorize requests using a reference monitor
1. Export logs
1. This service could be run from AWS Lamda or Google Cloud Functions to reduce costs
