# Use Python 3.10 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# # Install system dependencies and clean up in a single layer
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    # Install Playwright dependencies (if needed, specify more dependencies here)
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements.txt first for caching optimization
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browser (this installs necessary dependencies as well)
# RUN playwright install chromium

# Copy the rest of the application code
COPY . .


# Expose port 8003
EXPOSE 8003

# Start the application with uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
