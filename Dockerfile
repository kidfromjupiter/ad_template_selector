# Use smallest official Python Alpine image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

## Install system dependencies
RUN apk update && apk add --no-cache \
    git \
    build-base \
    libffi-dev \
    musl-dev \
    gcc \
    jpeg-dev \
    zlib-dev \
    python3-dev \
    py3-pip \
    && rm -rf /var/cache/apk/*

# Set work directory
WORKDIR /app

# Copy files
COPY . /app
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 2500

# Run the FastAPI server
CMD ["uvicorn", "backend_main:app", "--host", "0.0.0.0", "--port", "2500"]
