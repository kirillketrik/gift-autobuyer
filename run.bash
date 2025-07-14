#!/bin/bash

set -e

CONTAINER_NAME="telegram-gift-autobuyer"

echo "[*] Checking for Docker..."
if ! command -v docker &> /dev/null; then
    echo "[!] Docker not found. Installing Docker..."

    # Установка Docker (Ubuntu/Debian)
    sudo apt-get update
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg | \
        sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") \
      $(lsb_release -cs) stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

echo "[*] Ensuring Docker service is running..."
if ! sudo systemctl is-active --quiet docker; then
    sudo systemctl start docker
fi

echo "[*] Checking docker-compose plugin..."
if ! docker compose version &> /dev/null; then
    echo "[!] docker compose plugin not available. Please ensure Docker version >= 20.10 and plugin installed."
    exit 1
fi

echo "[*] Building and starting container in background..."
docker compose up --build -d

echo "[*] Waiting for container \"$CONTAINER_NAME\" to start..."
for i in {1..30}; do
    if docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        echo "[*] Container \"$CONTAINER_NAME\" is running."
        break
    fi
    sleep 2
done

if ! docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" | grep -q "$CONTAINER_NAME"; then
    echo "[!] Container \"$CONTAINER_NAME\" did not start in time."
    exit 1
fi

echo "[*] Attaching to container \"$CONTAINER_NAME\"..."
docker attach "$CONTAINER_NAME"
