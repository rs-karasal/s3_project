# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend/src /app/src/
COPY frontend /app/frontend/
COPY backend/.env /app/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:main_app", "--host", "0.0.0.0", "--port", "8000"]