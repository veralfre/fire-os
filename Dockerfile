# Django production Dockerfile using Gunicorn
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for best performance
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (if needed)
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Use Gunicorn with recommended settings for speed
CMD ["gunicorn", "fire_os.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2", "--worker-class=gthread", "--timeout=60", "--log-level=info"]
