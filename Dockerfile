# 🔧 Use official Python base image
FROM python:3.11-slim

# 🔐 Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 📁 Set working directory
WORKDIR /app

# 🔄 Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 📂 Copy all project files
COPY . .

# 🚀 Start the server with Gunicorn + Uvicorn worker
CMD ["gunicorn", "main:app", "--workers=8", "--threads=4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]