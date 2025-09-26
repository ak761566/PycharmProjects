
#/loader/job/multistepjob/v1/submitwithjson/{jobName}

CODE_202 = 202
# DESCRIPTION = "The request for MULTI-STEP Job has been accepted for processing, but the processing has not been completed"
JSON_RESPONSE_202 = {
  "jobId": "4248",
  "jobName": "LoaderJob",
  "jobOutputIds": "null",
  "jobInputIds": "null",
  "jobResult": "null",
  "jobStatus": "JOB_SUBMITTED",
  "jobInputParameters": "null",
  "jobStartTime": "null",
  "jobEndTime": "null",
  "errors": "null",
  "jobsLibError": "null",
  "steps": [],
  "className": "org.ithaka.portico.jobslib.utils.webservice.JobWebserviceResponse"
}

CODE_500 = 500
# DESCRIPTION = Something wrong with the jobs framework?
JSON_RESPONSE_500 = {
  "jobId": "string",
  "jobName": "string",
  "jobOutputIds": [
    "string"
  ],
  "jobInputIds": [
    "string"
  ],
  "jobResult": "string",
  "jobStatus": "string",
  "jobInputParameters": {
    "additionalProp1": {},
    "additionalProp2": {},
    "additionalProp3": {}
  },
  "jobStartTime": "2025-07-27T11:53:45.095Z",
  "jobEndTime": "2025-07-27T11:53:45.095Z",
  "errors": [
    {
      "contextId": "string",
      "contextType": "string",
      "severity": "string",
      "messageCode": "string",
      "messageText": "string",
      "additionalText": "string",
      "batchId": "string",
      "category": "string",
      "stepName": "string"
    }
  ],
  "jobsLibError": "string",
  "steps": [
    {
      "stepName": "string",
      "extCode": "string",
      "exitDescription": "string"
    }
  ],
  "className": "string"
}

# The underlaying resources are busy
JOB_RESPONSE_503 = {
  "jobId": "string",
  "jobName": "string",
  "jobOutputIds": [
    "string"
  ],
  "jobInputIds": [
    "string"
  ],
  "jobResult": "string",
  "jobStatus": "string",
  "jobInputParameters": {
    "additionalProp1": {},
    "additionalProp2": {},
    "additionalProp3": {}
  },
  "jobStartTime": "2025-07-27T11:53:45.096Z",
  "jobEndTime": "2025-07-27T11:53:45.096Z",
  "errors": [
    {
      "contextId": "string",
      "contextType": "string",
      "severity": "string",
      "messageCode": "string",
      "messageText": "string",
      "additionalText": "string",
      "batchId": "string",
      "category": "string",
      "stepName": "string"
    }
  ],
  "jobsLibError": "string",
  "steps": [
    {
      "stepName": "string",
      "extCode": "string",
      "exitDescription": "string"
    }
  ],
  "className": "string"
}
