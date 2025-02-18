#!/bin/bash

# Exit immediately if a command fails
set -e

echo "Starting MySQL container fix..."

# Step 1: Stop any running containers
echo "Stopping any running containers..."
docker-compose down

# Step 2: Find and remove the mysql_data volume
echo "Removing mysql_data volume (this will delete existing data)..."
VOLUME_NAME=$(docker volume ls -q | grep mysql_data)
if [ -n "$VOLUME_NAME" ]; then
  docker volume rm $VOLUME_NAME
  echo "Volume $VOLUME_NAME removed successfully."
else
  echo "No mysql_data volume found. Continuing..."
fi

# Step 3: Start fresh
echo "Starting containers with a fresh volume..."
docker-compose up -d

# Step 4: Check if containers started successfully
echo "Checking container status..."
sleep 5  # Give containers a moment to initialize
if docker-compose ps | grep "Up"; then
  echo "Success! MySQL container is running."
else
  echo "Container failed to start. Checking logs..."
  docker-compose logs
fi

echo "Script completed."