@echo off
echo 🔄 Restarting YouTube Channels Manager...

REM Stop containers
echo Stopping containers...
docker-compose down

REM Remove old containers and images
echo Cleaning up...
docker-compose rm -f
docker image prune -f

REM Rebuild and start
echo Rebuilding and starting...
docker-compose up --build -d

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

REM Check health
echo Checking health...
docker-compose ps

echo ✅ Restart complete!
echo 🌐 Web UI: http://localhost:5001/youtube-channels
echo 🔧 API: http://localhost:5001/api/youtube-channels
pause
