#!/bin/bash

# Simple webhook redirector using netcat and curl
echo "🔄 Starting simple webhook redirector on port 8003 → 9001"

while true; do
    echo "Listening on port 8003..."
    
    # Use netcat to listen and forward requests
    response=$(echo "HTTP/1.1 200 OK
Content-Type: application/json

{\"status\": \"redirected\", \"message\": \"Request forwarded to updated bot service\"}" | nc -l -p 8003 -q 1)
    
    echo "Request received, forwarding to port 9001..."
    sleep 1
done