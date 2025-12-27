FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install build deps required by some Python packages (kept minimal)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc build-essential libffi-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY app.py /app/
COPY src /app/src

# Ensure storage and log directories exist and are writable
RUN mkdir -p /app/storage/logs \
	&& useradd -ms /bin/bash appuser \
	&& chown -R appuser:appuser /app/storage /app/src

USER appuser

EXPOSE 8000

# Runtime command (do not use --reload in production)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
