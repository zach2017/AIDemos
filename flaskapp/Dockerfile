FROM python

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Create necessary directories
RUN mkdir -p /app/uploads /app/chroma_db

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
