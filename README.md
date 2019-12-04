# standaloneClient
## About
Check out standaloneClient pdf for a general explanation on how the program functions.
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
Open `standaloneClient_template.py`.  

Modify first lines with required data. You will need  

- fernet_key (You will need the same key for the decrypter. The key can be generated in a separate script with `Fernet.generate_key()`)
- orchestrator_function_name (Remember it for later)
- aws_access_key_id
- aws_secret_access_key
- region_name

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

Create 2 buckets with default config and remember their names (names must be all lowercase). One will be used for exfiltration and the other one for our templates.  

#### Sample Function Setup
Open `sampleFunction_template.py`.  
Modify first lines with required data. You will need  

- exfiltration_bucket_name

Compress the function (you can use Windows default compressor) and upload it to the template bucket created before. Remember the compressed function name. We should now have a sampleFunction_template.zip inside our template bucket.  

#### Lambda console setup
Create a lambda function called `<Insert orchestrator name>`.  
Give the function the role previously created. This can be done by scrolling down a bit one the function is created.  

Copy and paste the contents of `orchestrator_template.py` into the newly created lambda function.  

Modify first lines with required data. You will need  

- template_bucket_name
- compressed_function_name
- lambda_s3_iam_role (The ARN)

Increase the timeout of this function to 5 minute and memory to 512MB. The timeout will depend on the size of the file you plan on exfiltrating.  

#### Decrypter Setup
Files saved inside our exfiltration bucket are encrypted so... we ned a way to decrypt them. Lets se how to do this.  

Open `sampledecrypter_template.py`  

Modify first lines with required data. You will need  

- fernet_key
- aws_access_key_id
- aws_secret_access_key
- region_name
- exfiltration_bucket_name

