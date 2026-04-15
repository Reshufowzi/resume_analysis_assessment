# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (change if your app uses different port)
EXPOSE 5000

# Environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "run.py"]
