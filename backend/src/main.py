import os
import aiofiles
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from src.s3.s3_client import S3Client

load_dotenv()

main_app = FastAPI()

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@main_app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    part_size = 5 * 1024 * 1024     # Size of chunk is 5MB

    s3_client = S3Client(
        access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        bucket_name=os.getenv("AWS_BUCKET_NAME"),
    )

    async with s3_client.get_client() as client:
        await s3_client.create_multipart_upload(client, s3_client.bucket_name, file.filename)
        part_number = 1
        parts = []  # List of parts to complete multipart upload

        while chunk := await file.read(size=part_size):
            temp_file_path = f"/tmp/{file.filename}.part{part_number}"

            async with aiofiles.open(temp_file_path, 'wb') as temp_file:
                await temp_file.write(chunk)

            # Upload part to S3
            upload_task = asyncio.create_task(
                s3_client.upload_part(client, s3_client.bucket_name, file.filename, part_number, temp_file_path, part_size)
            )
            etag = (await upload_task)["ETag"]
            parts.append({"ETag": etag, "PartNumber": part_number})

            # Delete temp file after upload
            os.remove(temp_file_path)
            part_number += 1

        # Complete multipart upload
        await s3_client.complete_multipart_upload(client, s3_client.bucket_name, file.filename, parts)

    return {"info": f"file '{file.filename}' uploaded to S3"}


@main_app.get("/")
async def serve_frontend():
    with open("frontend/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
