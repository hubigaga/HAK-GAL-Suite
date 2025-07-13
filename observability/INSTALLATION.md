# 🚀 HAK-GAL LOKI OBSERVABILITY - INSTALLATION

## ⚡ SOFORT-INSTALLATION (EMPFOHLEN)

```bash
# 1. Navigate to observability directory
cd "D:\MCP Mods\HAK_GAL_SUITE\observability"

# 2. Run automated setup
python setup_observability.py

# 3. Wait for completion (~3-5 minutes)
# ✅ Services will start automatically

# 4. Access Grafana Dashboard
# URL: http://localhost:3000
# Login: admin / hak-gal-admin-2025
```

## 📋 MANUAL INSTALLATION

### **Schritt 1: Services starten**
```bash
cd observability
docker-compose -f docker-compose-loki.yml up -d
```

### **Schritt 2: Service-Health prüfen**
```bash
# Warten bis alle Services ready sind (~2-3 Minuten)
curl http://localhost:3100/ready    # Loki
curl http://localhost:9090/-/ready  # Prometheus  
curl http://localhost:3000/api/health # Grafana
```

### **Schritt 3: HAK-GAL Backend Integration**
```python
# In api.py hinzufügen:
from backend.logging_config import setup_hak_gal_logging
hak_gal_logger = setup_hak_gal_logging(log_level="INFO")
hak_gal_logger.info("HAK-GAL Backend started with observability")
```

### **Schritt 4: HAK-GAL Backend starten**
```bash
# Backend mit Logging starten
python api.py
```

### **Schritt 5: Test-Logs generieren**
```bash
# Frontend-Commands testen für Log-Generation
# - ask [query]
# - explain [concept]  
# - learn [fact]
# - show [info]
```

## 🎯 VALIDATION

### **Services Check:**
- ✅ **Loki:** http://localhost:3100 (Log storage)
- ✅ **Grafana:** http://localhost:3000 (Dashboards)  
- ✅ **Prometheus:** http://localhost:9090 (Metrics)

### **Dashboard Check:**
1. Open http://localhost:3000
2. Login: admin / hak-gal-admin-2025
3. Navigate: Dashboards → HAK-GAL → Backend Monitoring
4. Verify: Panels show data from HAK-GAL Backend

### **Logs Check:**
```bash
# Check log files exist
ls -la observability/logs/
# Should show: api.log, performance.log, sentry.log

# Check log content
tail -f observability/logs/api.log
# Should show JSON-formatted HAK-GAL logs
```

## 🐛 TROUBLESHOOTING

### **Docker Issues:**
```bash
# Check Docker status
docker ps | grep hak-gal

# Restart services
docker-compose -f docker-compose-loki.yml restart

# Check service logs
docker-compose -f docker-compose-loki.yml logs -f
```

### **Permission Issues (Linux/Mac):**
```bash
# Fix Grafana permissions
sudo chown -R 472:472 observability/data/grafana

# Fix Loki permissions  
sudo chown -R 10001:10001 observability/data/loki
```

### **Port Conflicts:**
```bash
# Check ports in use
netstat -tulpn | grep -E '3000|3100|9090'

# Stop conflicting services or change ports in docker-compose-loki.yml
```

## 📊 EXPECTED RESULTS

### **Nach erfolgreicher Installation:**

1. **Grafana Dashboard funktional:**
   - Error Rate: 0% (green)
   - Query Response Time: <1000ms (green)  
   - Backend Issues: 0 (green)
   - System Health: UP (green)

2. **Log-Streaming aktiv:**
   - Recent Error Logs Panel zeigt HAK-GAL logs
   - Live-Updates bei Frontend-Commands

3. **Performance-Tracking:**
   - Query Performance Histogram zeigt Response-Zeiten
   - Command Usage Pie Chart zeigt ask/explain/learn

### **Erste Test-Queries:**
```logql
# In Grafana → Explore → Loki:
{job="hak-gal-backend"}                    # Alle HAK-GAL logs
{job="hak-gal-backend", level="INFO"}      # Info logs
{job="hak-gal-backend"} | json | command   # Commands
```

## 🎉 SUCCESS CRITERIA

✅ **All services running:** docker ps shows 4 containers  
✅ **Grafana accessible:** Dashboard loads with data  
✅ **Logs flowing:** Recent logs appear in panels  
✅ **HAK-GAL integrated:** Backend logs to structured format  
✅ **Performance visible:** Query times tracked in dashboard  

## 📞 NEXT STEPS

Nach erfolgreicher Installation:

1. **Deploy BACKEND-7 & BACKEND-A fixes:**
   ```bash
   git add backend/services/advanced_relevance_adapter.py tools/hak_gal_relevance_filter.py
   git commit -m "🔧 Deploy critical backend fixes"
   git push origin main
   python api.py  # Restart with fixes
   ```

2. **Monitor Fix Success:**
   - Watch Grafana for ZERO new BACKEND-7/A events
   - Validate Error Rate stays <1%

3. **Optimize Performance:**
   - Analyze slow queries in dashboard
   - Set up custom alerts for business metrics

**🏆 OBSERVABILITY STACK: PRODUCTION READY!**
