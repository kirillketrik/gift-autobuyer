#!/bin/bash

set -e

SERVICE_NAME="telegram-gift-autobuyer"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
START_SCRIPT="/usr/local/bin/start_autobuyer.sh"
PROJECT_DIR="$(pwd)"   # Текущая директория запуска скрипта
RUN_SCRIPT="run.bash"  # Имя твоего скрипта запуска

USER_NAME=$(whoami)

echo "[*] Проверка прав пользователя"
if [ "$USER_NAME" = "root" ]; then
    echo "[!] Запускать скрипт от root не рекомендуется!"
fi

echo "[*] Копируем скрипт запуска в $START_SCRIPT"
cat > "$START_SCRIPT" <<EOF
#!/bin/bash
cd "$PROJECT_DIR" || exit 1
./$RUN_SCRIPT
EOF

chmod +x "$START_SCRIPT"

echo "[*] Создаём systemd сервис $SERVICE_PATH"
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Telegram Gift Autobuyer Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=$START_SCRIPT
Restart=always
RestartSec=10
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
Environment=PATH=/usr/bin:/bin:/usr/local/bin
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

echo "[*] Перезагружаем конфигурацию systemd"
sudo systemctl daemon-reload

echo "[*] Включаем автозапуск сервиса"
sudo systemctl enable "$SERVICE_NAME"

echo "[*] Запускаем сервис"
sudo systemctl start "$SERVICE_NAME"

echo "[*] Статус сервиса:"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "[*] Готово! Логи можно смотреть командой:"
echo "    journalctl -u $SERVICE_NAME -f"
