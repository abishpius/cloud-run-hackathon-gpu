# --- Ollama configuration environment variables ---
# Use the official ollama image as a base to get the binary and pull the model

FROM ollama/ollama:latest as ollama_builder
LABEL stage="ollama-builder"

# Install curl. It's used in the start_script.sh to check Ollama health status.
RUN apt-get update && apt-get install -y curl

# Listen to localhost, port 3000
ENV OLLAMA_HOST=http://localhost:3000

# Reduce logging verbosity
ENV OLLAMA_DEBUG=false

# Never unload model weights from the GPU
ENV OLLAMA_KEEP_ALIVE=-1

# Allow all origins
ENV OLLAMA_ORIGINS=*

# Define build argument for the model
ARG MODEL
ENV MODEL=alibayram/medgemma

# Store model weight files in /models
ENV OLLAMA_MODELS=/models
RUN /bin/ollama serve & sleep 5 && ollama pull $MODEL
# RUN ollama pull $MODEL
# ---------------------------------------------------

# Use official Python runtime as base image
FROM python:3.11

# Set working directory in container
WORKDIR /app

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for app and optionally Ollama
EXPOSE 8080 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run the application
# CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1
CMD bash -c "ollama serve & sleep 5 && uvicorn main:app --host 0.0.0.0 --port ${PORT}"

