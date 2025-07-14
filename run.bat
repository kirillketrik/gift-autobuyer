@echo off
setlocal

set "CONTAINER_NAME=telegram-gift-autobuyer"

echo Checking Docker installation...

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Docker not found. Downloading and installing Docker Desktop...

    set "DOCKER_URL=https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    set "INSTALLER=DockerInstaller.exe"

    powershell -Command "Invoke-WebRequest -Uri %DOCKER_URL% -OutFile %INSTALLER%"

    echo Running Docker installer...
    %INSTALLER% install --quiet

    echo Installation complete. Deleting installer...
    del %INSTALLER%

    echo Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

    timeout /t 10 >nul
) else (
    echo Docker is already installed.
)

rem Ждём пока Docker заработает
echo Waiting for Docker to become available...
set /a counter=0
:wait_loop
docker info >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Docker is ready.
) else (
    if %counter% GEQ 30 (
        echo [!] Docker did not start in time. Exiting.
        exit /b 1
    )
    set /a counter+=1
    timeout /t 2 >nul
    goto wait_loop
)

echo Starting docker-compose and building the image...
docker-compose up --build -d

rem Ожидаем появления и запуска контейнера
echo Waiting for container "%CONTAINER_NAME%" to start...
set /a counter=0
:container_check
docker ps --filter "name=%CONTAINER_NAME%" --filter "status=running" --format "{{.Names}}" | findstr /C:"%CONTAINER_NAME%" >nul
if %ERRORLEVEL% EQU 0 (
    echo Container %CONTAINER_NAME% is running.
) else (
    if %counter% GEQ 30 (
        echo [!] Container did not start in time. Exiting.
        exit /b 1
    )
    set /a counter+=1
    timeout /t 2 >nul
    goto container_check
)

echo Attaching to container %CONTAINER_NAME%...
docker attach %CONTAINER_NAME%

endlocal
