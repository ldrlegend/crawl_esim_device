#!/bin/bash

# Load environment variables from the .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    source .env
else
    echo ".env file not found, skipping loading environment variables."
fi

# Install ngrok if it's not already installed
if ! command -v ngrok &> /dev/null; then
    echo "Installing ngrok..."
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list
    apt update && apt install ngrok -y
fi

# Set ngrok auth token if provided
if [ -n "$NGROK_AUTH_TOKEN" ]; then
    echo "Configuring ngrok with the provided auth token..."
    ngrok config add-authtoken "$NGROK_AUTH_TOKEN"
fi

# Start the uvicorn server in the background
echo "Starting uvicorn server on port 8003..."
uvicorn api:app --host 0.0.0.0 --port 8003 &

# Wait for a moment for the server to start
sleep 5

# Check if ngrok should be started
if [ -n "$NGROK_AUTH_TOKEN" ] && [ -n "$NGROK_DOMAIN" ]; then
    echo "Starting ngrok tunnel..."
    echo "Using domain: $NGROK_DOMAIN"
    echo "Using authtoken: ${NGROK_AUTH_TOKEN:0:10}..."  # Show first 10 chars for security

    # Kill any existing ngrok processes
    pkill ngrok 2>/dev/null || true
    sleep 2  # Wait for previous ngrok processes to terminate

    # Verify ngrok configuration
    echo "Verifying ngrok configuration..."
    ngrok config check

    # Start ngrok with better error handling
    echo "Starting ngrok tunnel to domain: $NGROK_DOMAIN"
    if ngrok http --domain="$NGROK_DOMAIN" 8003; then
        echo "Ngrok tunnel started successfully."
    else
        echo "Ngrok failed to start. The server is still running on port 8003."
        echo "You can access the API directly at http://localhost:8003"
        echo "Or use port forwarding: docker port <container_name>"
        echo "Check ngrok logs for more details."
    fi
else
    echo "Ngrok not configured. Server is running on port 8003."
    echo "You can access the API directly at http://localhost:8003"
    echo "To enable ngrok, set NGROK_AUTH_TOKEN and NGROK_DOMAIN environment variables."
fi

# Keep the container running (this waits for all background processes)
wait
