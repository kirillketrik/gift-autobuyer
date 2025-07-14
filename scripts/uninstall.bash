#!/bin/bash

set -e

CONTAINER_NAME="telegram-gift-autobuyer"
IMAGE_NAME="telegram-gift-autobuyer"
SERVICE_NAME="telegram-gift-autobuyer"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

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
IMAGE_IDS=$(docker images --filter=reference="$IMAGE_NAME*" --format "{{.ID}}")

if [ -n "$IMAGE_IDS" ]; then
    for IMAGE_ID in $IMAGE_IDS; do
        echo "[*] Удаление образа ID: $IMAGE_ID"
        docker rmi "$IMAGE_ID"
    done
    echo "[*] Образ(ы) удалены."
else
    echo "[!] Образ \"$IMAGE_NAME\" не найден."
fi

echo "[*] Проверка наличия systemd-сервиса \"$SERVICE_NAME\"..."
if [ -f "$SERVICE_PATH" ]; then
    echo "[*] Отключение автозапуска и остановка сервиса..."
    sudo systemctl stop "$SERVICE_NAME" || true
    sudo systemctl disable "$SERVICE_NAME" || true
    echo "[*] Удаление systemd unit файла..."
    sudo rm "$SERVICE_PATH"
    echo "[*] Перезагрузка systemd..."
    sudo systemctl daemon-reload
    echo "[*] Сервис удалён."
else
    echo "[*] Сервис не найден."
fi
