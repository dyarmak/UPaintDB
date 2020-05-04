# Create the necessary functions for working with AWS S3 Buckets

import boto3
from botocore.exceptions import ClientError


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    print("upload_file() successful")
    return True

def download_file(file_name, bucket, output_filename):
    """
    Function to download a given file from an S3 bucket to the cwd
    """
    resource = boto3.resource('s3')
    my_bucket = resource.Bucket(bucket)
    local_filename = output_filename
    my_bucket.download_file(file_name, local_filename)

    # s3 = boto3.resource('s3')
    # output = f"downloads/{file_name}"
    # s3.Bucket(bucket).download_file(file_name, output)

    return local_filename

def list_files(bucket):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client('s3')
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)

    return contents