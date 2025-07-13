# 🐳 DOCKER INSTALLATION FÜR HAK-GAL OBSERVABILITY

## ⚡ WINDOWS DOCKER INSTALLATION

### **Schritt 1: Docker Desktop Download**
1. **Download:** https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe
2. **Systemanforderungen:**
   - Windows 10/11 64-bit
   - WSL 2 Backend (automatisch installiert)
   - 4GB RAM minimum

### **Schritt 2: Installation**
```powershell
# 1. Docker Desktop Installer ausführen
# 2. Installation durchlaufen (5-10 Minuten)
# 3. System-Neustart wenn angefordert
# 4. Docker Desktop starten
```

### **Schritt 3: Installation validieren**
```powershell
# Nach Installation und Neustart:
docker --version
docker-compose --version

# Sollte zeigen:
# Docker version 24.x.x
# Docker Compose version 2.x.x
```

### **Schritt 4: HAK-GAL Observability**
```powershell
cd "D:\MCP Mods\HAK_GAL_SUITE\observability"
.\setup.bat
```

## 🔄 **ALTERNATIVE: LOKALES LOGGING (OHNE DOCKER)**

Falls Docker nicht gewünscht, verwenden Sie lokales Python-Logging:

### **Vereinfachte Logging-Konfiguration:**
```python
# In api.py hinzufügen:
import logging
import json
from datetime import datetime

# Setup basic JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
    handlers=[
        logging.FileHandler('hak_gal_backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('hak_gal')
logger.info("HAK-GAL Backend started with basic logging")
```

### **Log-Monitoring:**
```powershell
# Logs in Echtzeit anzeigen
Get-Content hak_gal_backend.log -Wait -Tail 10

# Fehler filtern
Get-Content hak_gal_backend.log | Select-String "ERROR"

# BACKEND-Issues finden
Get-Content hak_gal_backend.log | Select-String "BACKEND-"
```

## 📊 **EMPFEHLUNG: PRIORISIERUNG**

### **SOFORT (OHNE DOCKER):**
1. ✅ **Backend-Fixes deployen** - Löst kritische BACKEND-7/A Issues
2. ✅ **Frontend-Testing** - Validiert Fix-Erfolg via Sentry
3. ✅ **Basic Python Logging** - Einfache Log-Dateien

### **SPÄTER (MIT DOCKER):**
1. 🔄 **Docker Desktop Installation** - Wenn Observability gewünscht
2. 🔄 **Grafana/Loki Setup** - Advanced Monitoring  
3. 🔄 **Performance Optimization** - Dashboard & Alerting

## 🎯 **BUSINESS-IMPACT VERGLEICH**

| Action | Impact | Aufwand | **Priorität** |
|--------|--------|---------|---------------|
| **Backend-Fixes** | 🔴 KRITISCH | 2 Min | 🥇 **SOFORT** |
| **Docker Installation** | 🟡 NÜTZLICH | 30 Min | 🥈 **SPÄTER** |
| **Observability Stack** | 🟢 OPTIMIZATION | 60 Min | 🥉 **OPTIONAL** |

## ✅ **RECOMMENDED ACTION**

**JETZT:** Backend-Fixes deployen (funktioniert ohne Docker)
**SPÄTER:** Docker installieren wenn erweiterte Monitoring gewünscht

```powershell
# SOFORTIGE AKTION (ohne Docker):
cd "D:\MCP Mods\HAK_GAL_SUITE"
git add backend/services/advanced_relevance_adapter.py tools/hak_gal_relevance_filter.py
git commit -m "🔧 Deploy critical BACKEND-7 and BACKEND-A fixes"
git push origin main
python api.py
```

**ERGEBNIS:** BACKEND-7 und BACKEND-A Issues werden sofort gelöst, Sentry zeigt Verbesserung binnen Minuten.
