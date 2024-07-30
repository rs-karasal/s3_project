import os
import aiofiles
import asyncio
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
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
    part_size = 5 * 1024 * 1024  # 5MB
    s3_client = S3Client(
        access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        bucket_name=os.getenv("AWS_BUCKET_NAME"),
    )

    async with s3_client.get_client() as client:
        # Начало мультизагрузки в S3
        await s3_client.create_multipart_upload(client, s3_client.bucket_name, file.filename)
        part_number = 1
        parts = []

        try:
            async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:
                while chunk := await file.read(part_size):
                    # Запись части файла во временный файл
                    await temp_file.write(chunk)

                    # Перемещение курсора в начало временного файла для чтения данных
                    await temp_file.seek((part_number - 1) * part_size)
                    
                    # Загрузка части файла в S3
                    async with aiofiles.open(temp_file.name, 'rb') as part_file:
                        part_chunk = await part_file.read(part_size)
                        response = await s3_client.upload_part(client, s3_client.bucket_name, file.filename, part_number, part_chunk)
                        parts.append({"ETag": response["ETag"], "PartNumber": part_number})
                        part_number += 1

        finally:
            # Удаление временного файла после завершения
            os.remove(temp_file.name)

        # Завершение мультизагрузки в S3
        await s3_client.complete_multipart_upload(client, s3_client.bucket_name, file.filename, parts)

    return {"info": f"file '{file.filename}' uploaded to S3"}

@main_app.get("/")
async def serve_frontend():
    with open("frontend/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)