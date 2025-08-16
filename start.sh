#!/bin/bash
set -e

# Check for docker-compose or fallback to 'docker compose'
if command -v docker-compose &> /dev/null; then
    docker-compose up --build
elif docker compose version &> /dev/null; then
    docker compose up --build
else
    echo "docker-compose or 'docker compose' not found. Attempting to install docker-compose..."
    # Try to install docker-compose (Linux/macOS only)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        if command -v docker-compose &> /dev/null; then
            echo "docker-compose installed successfully."
            docker-compose up --build
        else
            echo "Failed to install docker-compose. Please install Docker manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        if command -v docker-compose &> /dev/null; then
            echo "docker-compose installed successfully."
            docker-compose up --build
        else
            echo "Failed to install docker-compose. Please install Docker manually."
            exit 1
        fi
    else
        echo "Automatic installation not supported for your OS. Please install Docker manually."
        exit 1
    fi
fi
