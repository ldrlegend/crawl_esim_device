# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Playwright (headless Chromium)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgdk-pixbuf-xlib-2.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    fonts-unifont \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Playwright
RUN pip install playwright

# Install Chromium browser (Playwright will download this automatically)
RUN playwright install chromium

# Copy requirements.txt first for caching optimization
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose FastAPI port
EXPOSE 8003

# Start the application with uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
