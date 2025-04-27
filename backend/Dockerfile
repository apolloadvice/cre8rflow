FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Set working directory
WORKDIR /app

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy application code
COPY ./app /app/app

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV MODULE_NAME="app.main"
ENV VARIABLE_NAME="app"
ENV WORKERS_PER_CORE=1
ENV MAX_WORKERS=4

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 