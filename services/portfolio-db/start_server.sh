#!/bin/bash

# Parse command line arguments
FOREGROUND=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--foreground)
            FOREGROUND=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-f|--foreground]"
            exit 1
            ;;
    esac
done

# Kill any existing server on port 8080
pkill -f portfolio-db 2>/dev/null || true
sleep 1

# Build the server
echo "Building portfolio-db..."
go build -o portfolio-db

# Start the server
if [ "$FOREGROUND" = true ]; then
    echo "Starting MCP server on port 8080 in foreground..."
    ./portfolio-db
else
    echo "Starting MCP server on port 8080 in background..."
    nohup ./portfolio-db > server.log 2>&1 &

    # Wait a moment for server to start
    sleep 2

    # Check if it's running
    if pgrep -f portfolio-db > /dev/null; then
        echo "Server started successfully (PID: $(pgrep -f portfolio-db))"

        # Hit the health check endpoint
        echo "Checking health endpoint..."
        if curl -f -s http://localhost:8080/health > /dev/null; then
            echo "Health check passed - server is ready!"
        else
            echo "Health check failed - server may not be ready"
            exit 1
        fi
    else
        echo "Failed to start server"
        exit 1
    fi
fi
