# Dockerfile
FROM python:3.11-slim

# Keep Python output unbuffered & skip .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Flask’s default port is 5000
EXPOSE 5000

# Start the app (make sure app.py runs on 0.0.0.0:5000)
CMD ["python", "app.py"]
