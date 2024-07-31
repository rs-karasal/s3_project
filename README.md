# S3 Multipart File Upload Service

This project is a FastAPI-based service that supports multipart file uploads to Amazon S3. The service divides large files into smaller chunks, uploads each chunk asynchronously, and removes temporary files after successful uploads.

## Features

- **Multipart File Upload**: Upload large files by splitting them into smaller chunks.
- **Asynchronous Operations**: Utilize asyncio and aiofiles for non-blocking file operations.
- **Resource Efficient**: Removes temporary chunk files after successful uploads to minimize disk usage.
- **CORS Support**: Configured to allow cross-origin requests.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- An S3 bucket (or S3-compatible storage) with appropriate access permissions

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/s3-multipart-upload.git
    cd s3-multipart-upload
    ```

2. Create a `.env` file in the project root directory with your S3 credentials and bucket details:
    ```env
    AWS_ACCESS_KEY_ID=your-access-key-id
    AWS_SECRET_ACCESS_KEY=your-secret-access-key
    AWS_ENDPOINT_URL=https://your-s3-endpoint-url
    AWS_BUCKET_NAME=your-bucket-name
    ```

3. Build and run the Docker container:
    ```sh
    docker build -t s3-upload-app .
    docker run -d -p 8000:8000 --memory=512m --name s3-upload-app s3-upload-app
    ```

4. The service will be available at `http://localhost:8000`.

### Usage

#### Upload File

- **Endpoint**: `POST /upload/`
- **Form Data**: 
  - `file`: The file to upload

Example using `curl`:
```sh
curl -X POST "http://localhost:8000/upload/" -F "file=@path/to/your/file"