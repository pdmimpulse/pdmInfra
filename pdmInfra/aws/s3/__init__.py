import logging
import boto3
import json
from botocore.exceptions import ClientError

s3 = boto3.client("s3") 
region = "eu-central-1" 

def create_bucket(bucket_name):
    location = {'LocationConstraint': region}
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

def list_buckets():
    return [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]

def delete_bucket(bucket_name):
    s3.delete_bucket(Bucket=bucket_name, region_name = region)

def s3_put_object(bucket_name, key, body):
    if type(body) in [dict, list]:
        upload = json.dumps(body)
    elif type(body) == str:
        upload = body

    try:
        s3.put_object(Bucket=bucket_name, Key=key, Body=upload)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def s3_get_object(bucket_name, key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    file_content = response['Body'].read().decode('utf-8')
    return file_content

def s3_delete_object(bucket_name, key):
    s3.delete_object(Bucket=bucket_name, Key=key)

def s3_list_objects(bucket_name):
    return s3.list_objects_v2(Bucket=bucket_name)

