import aiofiles
from aiobotocore.session import get_session
from contextlib import asynccontextmanager


class S3Client:
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_part(self, client, bucket_name, object_name, part_number, temp_file_path, part_size):
        async with aiofiles.open(temp_file_path, 'rb') as part_file:
            data = await part_file.read(part_size)
            response = await client.upload_part(
                Bucket=bucket_name,
                Key=object_name,
                PartNumber=part_number,
                UploadId=self.upload_id,
                Body=data
            )
        return response

    async def create_multipart_upload(self, client, bucket_name, object_name):
        response = await client.create_multipart_upload(Bucket=bucket_name, Key=object_name)
        self.upload_id = response["UploadId"]

    async def complete_multipart_upload(self, client, bucket_name, object_name, parts):
        response = await client.complete_multipart_upload(
            Bucket=bucket_name,
            Key=object_name,
            UploadId=self.upload_id,
            MultipartUpload={"Parts": parts}
        )
        return response
