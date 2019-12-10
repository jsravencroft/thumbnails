# Introduction

This is the Thumbnailer module.  When run directly `python3 thumbnailer` it polls the SQS queue for new jobs.  The job contains information about an image which must be made into a thumbnail of 100x100 pixels.

# API CALLS

This system has no inbound network traffic, so it has no API calls.  It polls the QUEUE based on the information in the shell environment:
* SQS_ENDPOINT:  The API endpoint for SQS
* SQS_QUEUE:     The queue to monitor
* SQS_QUEUE_URL: A convenience value since Boto calls utilize the QueueUrl

# Issues
* A test with polling is needed.  Current test only recieves a job, tests processing of the job, then writes the job result.
* It's possible a Thumbnail could fail being created, but some failures may justify a retry, some may require failing the entire job.

# Opportunities Roadmap (In Order of Priority)
1. Allow and honor output format for thumbnails, now it's always JPG
1. Read a job['completion_hook'] and make an outbound API call to alert users their job is finished
