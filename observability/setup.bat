@echo off
echo 🚀 HAK-GAL OBSERVABILITY - WINDOWS SETUP
echo ==========================================

echo.
echo 📁 Current directory: %CD%
echo.

echo 🔍 Checking Docker...
docker --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker not found! Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker found
echo.

echo 🔍 Checking Docker Compose...
docker-compose --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker Compose not found!
    pause
    exit /b 1
)

echo ✅ Docker Compose found
echo.

echo 📁 Creating logs directory...
if not exist "logs" mkdir logs
echo ✅ Logs directory ready

echo.
echo 🚀 Starting HAK-GAL Observability Services...
echo Command: docker-compose -f docker-compose-loki.yml up -d

docker-compose -f docker-compose-loki.yml up -d

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start services!
    echo.
    echo 🔍 Checking for errors...
    docker-compose -f docker-compose-loki.yml logs
    pause
    exit /b 1
)

echo ✅ Services started successfully!
echo.

echo 📊 Checking service status...
docker-compose -f docker-compose-loki.yml ps

echo.
echo ⏳ Waiting 30 seconds for services to initialize...
timeout /t 30 /nobreak

echo.
echo 🧪 Testing service accessibility...
echo.

echo Testing Loki...
curl -s -o nul -w "Loki: %%{http_code}\n" http://localhost:3100/ready

echo Testing Grafana...
curl -s -o nul -w "Grafana: %%{http_code}\n" http://localhost:3000/api/health

echo Testing Prometheus...
curl -s -o nul -w "Prometheus: %%{http_code}\n" http://localhost:9090/-/ready

echo.
echo ================================================================
echo 🎉 HAK-GAL OBSERVABILITY SETUP COMPLETED
echo ================================================================
echo.
echo 📊 Service URLs:
echo   🎯 Grafana:    http://localhost:3000
echo      Login:      admin / hak-gal-admin-2025
echo   📈 Prometheus: http://localhost:9090
echo   📜 Loki:       http://localhost:3100
echo.
echo 🔧 Next Steps:
echo   1. Open Grafana: http://localhost:3000
echo   2. Login with: admin / hak-gal-admin-2025
echo   3. Go to Dashboards → Browse → HAK-GAL
echo   4. Start HAK-GAL Backend: python ../api.py
echo   5. Test commands in Frontend
echo.
echo 📋 Troubleshooting:
echo   • Service logs: docker-compose -f docker-compose-loki.yml logs
echo   • Restart:      docker-compose -f docker-compose-loki.yml restart
echo   • Stop:         docker-compose -f docker-compose-loki.yml down
echo.

echo 🌐 Opening Grafana in browser...
start http://localhost:3000

echo.
pause
