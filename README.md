S3 connection project


Для запуска контейнера с ограничениями памяти в 512 МБ:
1) docker build -t s3-upload-app .
2) docker run -d -p 8000:8000 --memory=512m --name s3-upload-app s3-upload-app