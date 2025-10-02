#!/bin/bash

echo "🔄 Restarting YouTube Channels Manager..."

# Stop containers
echo "Stopping containers..."
docker-compose down

# Remove old containers and images
echo "Cleaning up..."
docker-compose rm -f
docker image prune -f

# Rebuild and start
echo "Rebuilding and starting..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check health
echo "Checking health..."
docker-compose ps

echo "✅ Restart complete!"
echo "🌐 Web UI: http://localhost:5001/youtube-channels"
echo "🔧 API: http://localhost:5001/api/youtube-channels"
