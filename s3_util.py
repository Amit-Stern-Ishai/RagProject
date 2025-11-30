import boto3
from botocore.exceptions import ClientError
from flask import jsonify

from environment_variables import S3_BUCKET

s3 = boto3.client("s3")

def upload_files(files_to_upload):
    for file_to_upload in files_to_upload:
        key = file_to_upload.name

        try:
            s3.upload_fileobj(
                Fileobj=file_to_upload,
                Bucket=S3_BUCKET,
                Key=key,
                ExtraArgs={"ContentType": file_to_upload.content_type}
            )
        except ClientError as e:
            return jsonify({"error": str(e)}), 500
