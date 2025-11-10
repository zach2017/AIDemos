FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    pyspark==3.5.0 \
    pyiceberg[s3fs,pyarrow]==0.6.1 \
    chromadb==0.4.18 \
    ollama==0.1.7 \
    boto3==1.34.27 \
    pandas==2.1.4 \
    requests==2.31.0

# Copy application files
COPY . /app/

CMD ["tail", "-f", "/dev/null"]
