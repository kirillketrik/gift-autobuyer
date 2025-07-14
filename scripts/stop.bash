#!/bin/bash

set -e

CONTAINER_NAME="telegram-gift-autobuyer"

echo "[*] Проверка, запущен ли контейнер \"$CONTAINER_NAME\"..."
if docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[*] Остановка контейнера \"$CONTAINER_NAME\"..."
    docker stop "$CONTAINER_NAME"
    echo "[*] Контейнер остановлен."
else
    echo "[!] Контейнер \"$CONTAINER_NAME\" не запущен."
fi
