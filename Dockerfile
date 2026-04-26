# Use the official Python 3.10 slim image
FROM python:3.10-slim

# Copy uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies using uv
# We use --system to install directly into the container's Python environment
# and leverage cache mount for speed
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv pip install --system -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data

# Expose the port (used by dashboard)
EXPOSE 8000

# Default command (usually overridden in docker-compose)
CMD ["python", "-m", "src.main"]



