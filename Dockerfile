# Use the official Python image as a base
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libtiff5-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install PDM
RUN pip install pdm

# Copy the PDM project files to the working directory
COPY pyproject.toml pdm.lock ./
COPY requirements.txt ./
COPY README.md ./

# Install dependencies using PDM and pip (if needed)
RUN pdm install --production

# Copy the application code, scraper script, and entry point script
COPY . .

# Ensure the data directory exists and is writable
RUN mkdir -p data

# Make the entry point script executable
RUN chmod +x entrypoint.sh

# Expose the port FastAPI runs on
EXPOSE 8000

# Set the entry point to the entry point script
ENTRYPOINT ["./entrypoint.sh"]
