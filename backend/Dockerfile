# Use an official Python image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install spaCy models
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download nl_core_news_sm

# Copy the rest of the code
COPY . /app/

# Default command (can be overridden in Railway settings)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
