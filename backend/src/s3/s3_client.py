import asyncio
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

    async def upload_part(self, client, bucket_name, object_name, part_number, data):
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

    async def upload_file(self, file_path: str):
        object_name = file_path.split("/")[-1]
        part_size = 5 * 1024 * 1024  # 5MB
        parts = []
        async with self.get_client() as client:
            await self.create_multipart_upload(client, self.bucket_name, object_name)
            part_number = 1
            async with aiofiles.open(file_path, 'rb') as file:
                while chunk := await file.read(part_size):
                    future = asyncio.ensure_future(
                        self.upload_part(client, self.bucket_name, object_name, part_number, chunk)
                    )
                    parts.append({"ETag": (await future)["ETag"], "PartNumber": part_number})
                    part_number += 1
            await self.complete_multipart_upload(client, self.bucket_name, object_name, parts)