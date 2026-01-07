FROM python:3.11-slim

# Install system dependencies
# libgl1-mesa-glx is often needed for opencv/docling dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir docling pdfplumber pandas pydantic structlog click python-dotenv psycopg2-binary sqlalchemy alembic

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /data/pdfs /data/csv /data/processed /data/failed

# Set environment variables
ENV PYTHONPATH=/app

# Default command
CMD ["python", "-m", "pdf_processor.cli", "process"]
