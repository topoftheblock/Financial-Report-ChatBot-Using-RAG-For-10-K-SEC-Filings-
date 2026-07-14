# Use an official Python runtime as a parent image (Python 3.10+ required per your README)
FROM python:3.10-slim

# Set environment variables to ensure Python output is logged directly and to prevent writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# (Added standard build tools which are often required by vector DBs like Chroma or parsing libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# (We copy this after requirements to leverage Docker's layer caching)
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Add a healthcheck to ensure the container is running properly
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to run the Streamlit application
CMD ["streamlit", "run", "app/main.py"]