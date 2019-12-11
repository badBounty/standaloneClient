# AWS Lambda Exfil Tool [PoC]
## About
The program follows the following diagram. Explanation on how each part functions is present on standaloneClient pdf file.  

![StandaloneClient diagram](Standalone_client_1.png?raw=true "Standalone Client Diagram")

Here we have a small PoC on how the program works

![StandaloneClientGif](standaloneClient.gif)

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

###### Note: Use python 3.x  

#### IAM Console
Go to AWS IAM console and create a role (Remember the ARN name) with the following permissions:  

- AWSLambdaFullAccess
- AmazonS3FullAccess
- CloudWatchFullAccess

###### Run `pip install -r requirements.txt`

###### Run `py setup.py` and follow the prompts
