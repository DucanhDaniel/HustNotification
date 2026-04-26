# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_SYSTEM_PYTHON=1


# Copy dependency files
COPY requirements.txt ./

# Install dependencies to system Python using uv
RUN uv pip install --system --no-cache -r requirements.txt


# Copy the rest of the application code into the container
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data

# Expose the port the dashboard runs on
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "src.main"]

