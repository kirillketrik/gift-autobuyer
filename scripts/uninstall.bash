#!/bin/bash

set -e

CONTAINER_NAME="telegram-gift-autobuyer"
IMAGE_NAME="telegram-gift-autobuyer"  # По умолчанию совпадает с именем папки/проекта

echo "[*] Проверка, запущен ли контейнер \"$CONTAINER_NAME\"..."
if docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[*] Остановка контейнера..."
    docker stop "$CONTAINER_NAME"
fi

if docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[*] Удаление контейнера..."
    docker rm "$CONTAINER_NAME"
fi

echo "[*] Поиск и удаление образа \"$IMAGE_NAME\"..."
IMAGE_ID=$(docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep "^${IMAGE_NAME}:" | awk '{print $2}')

if [ -n "$IMAGE_ID" ]; then
    echo "[*] Удаление образа ID: $IMAGE_ID"
    docker rmi "$IMAGE_ID"
    echo "[*] Образ удалён."
else
    echo "[!] Образ \"$IMAGE_NAME\" не найден."
fi
