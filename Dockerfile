# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spacy model (IMPORTANT)
RUN python -m spacy download en_core_web_sm

# Expose port
EXPOSE 5000

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "run.py"]
