import json
import boto3
import math
import uuid
import sys


def lambda_handler(event, context):
    
    aws_s3 = boto3.resource('s3')
    
    #We take partitions amount from the client
    partitions_amount = int(event['partitions'])
    
    #Client for using AWS Lambda
    aws_lambda = boto3.client('lambda')
    lambda_list = []
    for i in range(partitions_amount):
        
        #UUID Function name
        lambda_name = str(uuid.uuid1())
        
        #Function create
        aws_lambda.create_function(
        FunctionName = lambda_name,
        Runtime = 'python3.7',
        Role = lambda_s3_iam_role,
        Handler = 'sampleFunction_template.lambda_handler',
        Code = {
            'S3Bucket': template_bucket_name,
            'S3Key': compressed_function_name
            },
        Timeout = 30,
        MemorySize = 512 
        )
        
        lambda_list.append(lambda_name)
        
    
    return{
        'names' : lambda_list
    }

