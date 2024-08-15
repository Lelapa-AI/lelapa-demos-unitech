# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install PDM
RUN pip install pdm

# Copy the PDM project files to the working directory
COPY pyproject.toml pdm.lock ./

# Install dependencies using PDM
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
