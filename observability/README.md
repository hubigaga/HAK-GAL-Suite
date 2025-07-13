# 🔍 HAK-GAL OBSERVABILITY STACK

**Production-Ready Logging, Monitoring & Alerting für HAK-GAL Backend**

## 📋 ÜBERBLICK

Vollständiger Observability-Stack mit:
- **📊 Grafana Loki** - Zentrales Log-Management
- **📈 Prometheus** - Metrics & Monitoring  
- **🎯 Grafana** - Dashboards & Visualization
- **🚨 Alerting** - Proaktive Problem-Detection

## ⚡ QUICK START

### **1-Command Setup:**
```bash
cd observability
python setup_observability.py
```

### **Manual Setup:**
```bash
# 1. Start Services
docker-compose -f docker-compose-loki.yml up -d

# 2. Verify Services
curl http://localhost:3100/ready  # Loki
curl http://localhost:9090/-/ready # Prometheus  
curl http://localhost:3000/api/health # Grafana

# 3. Access Dashboards
open http://localhost:3000  # Grafana (admin/hak-gal-admin-2025)
```

## 🏗️ ARCHITECTURE

```
HAK-GAL Backend (api.py)
    ↓ (structured JSON logs)
Promtail (log collection)
    ↓ (push logs)
Loki (log storage)
    ↓ (query logs)
Grafana (visualization)
    ↑ (metrics)
Prometheus (metrics storage)
    ↑ (scrape metrics)  
HAK-GAL + Promtail metrics
```

## 📊 GRAFANA DASHBOARDS

### **HAK-GAL Backend Monitoring**
- **Error Rate** - Real-time error tracking
- **Query Response Time** - 95th percentile performance
- **Backend Issues** - BACKEND-A/B/C/D/5/6/7/8/9 tracking
- **System Health** - Service availability
- **Recent Error Logs** - Live error streaming
- **Query Performance** - Response time heatmaps
- **Command Usage** - ask/explain/learn/show statistics
- **Async Operations** - Advanced Tools monitoring

**Access:** http://localhost:3000/d/hak-gal-backend/

## 🔧 HAK-GAL LOGGING INTEGRATION

### **Automatic Integration:**
```python
# In api.py (added automatically by setup)
from backend.logging_config import setup_hak_gal_logging
hak_gal_logger = setup_hak_gal_logging(log_level="INFO")
```

### **Manual Usage:**
```python
from backend.logging_config import get_hak_gal_logger

logger = get_hak_gal_logger("api")

# Command logging
logger.log_command("explain AI", user_id="user123", query_time_ms=1250.5)

# Performance logging  
logger.log_performance("relevance_query", 850.2, memory_mb=25.4)

# Backend issue logging
logger.log_backend_issue("A", "metadata error", error_type="api")

# Context manager for performance
with LogPerformance(logger, "complex_operation"):
    # Your code here
    pass
```

## 📁 LOG FILES

```
observability/logs/
├── api.log              # Main HAK-GAL logs
├── performance.log      # Performance metrics  
├── sentry.log          # Sentry correlation
├── advanced_tools.log  # Advanced Tools logs
└── hak-gal-loki.log    # Loki-compatible format
```

## 🚨 ALERTING RULES

### **Critical Alerts:**
- **HAKGALHighErrorRate** - Error rate > 10%
- **HAKGALBackendIssue** - New BACKEND-* issues
- **HAKGALServiceDown** - Service unavailable
- **HAKGALLearningSystemFailures** - Learn command failures

### **Warning Alerts:**
- **HAKGALSlowQueries** - 95th percentile > 5s
- **HAKGALAsyncioErrors** - Asyncio issues
- **HAKGALMetadataErrors** - RelevanceResult errors
- **HAKGALCommandTimeouts** - 45s timeouts

### **Info Alerts:**
- **HAKGALHighQueryVolume** - High usage patterns
- **HAKGALLowCacheHitRate** - Performance optimization

## 🔍 LOG QUERIES

### **Loki Query Examples:**

```logql
# All HAK-GAL errors
{job="hak-gal-backend", level="ERROR"}

# Backend issues
{job="hak-gal-backend"} |= "BACKEND-"

# Slow queries
{job="hak-gal-backend"} | json | query_time_ms > 1000

# Specific commands
{job="hak-gal-backend"} | json | command =~ "ask|explain"

# Asyncio errors
{job="hak-gal-backend"} | json | error_type = "asyncio"

# Performance logs
{job="hak-gal-performance"} | json | duration_ms > 500
```

### **Prometheus Query Examples:**

```promql
# Error rate
rate(hak_gal_log_lines_total{level="ERROR"}[5m])

# Query latency percentiles
histogram_quantile(0.95, rate(hak_gal_query_duration_bucket[5m]))

# Backend issue count
sum by (backend_issue) (hak_gal_backend_errors)

# Service availability
up{job="hak-gal-backend"}
```

## 📈 PERFORMANCE OPTIMIZATION

### **Loki Retention:**
- **Development:** 14 days (336h)
- **Production:** Adjust in `loki-config.yaml`

### **Log Rotation:**
- **API logs:** 10MB, 5 files
- **Performance:** 20MB, 3 files  
- **Loki logs:** 50MB, 3 files

### **Resource Limits:**
```yaml
# docker-compose-loki.yml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

## 🔒 SECURITY CONFIGURATION

### **Grafana Security:**
- **Default Admin:** admin/hak-gal-admin-2025
- **Sign-up disabled:** GF_USERS_ALLOW_SIGN_UP=false
- **Change password** in production!

### **Network Security:**
```yaml
# Internal network only
networks:
  hak-gal-observability:
    internal: true  # Add for production
```

## 🐛 TROUBLESHOOTING

### **Services Not Starting:**
```bash
# Check logs
docker-compose -f docker-compose-loki.yml logs

# Check disk space
df -h

# Check permissions
ls -la data/
```

### **Loki Not Receiving Logs:**
```bash
# Check Promtail
docker logs hak-gal-promtail

# Test log ingestion
curl -X POST "http://localhost:3100/loki/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{"streams":[{"stream":{"job":"test"},"values":[["1234567890000000000","test message"]]}]}'
```

### **Grafana Dashboard Issues:**
```bash
# Restart Grafana
docker restart hak-gal-grafana

# Check datasources
curl -u admin:hak-gal-admin-2025 http://localhost:3000/api/datasources
```

### **Performance Issues:**
```bash
# Monitor resource usage
docker stats hak-gal-loki hak-gal-promtail hak-gal-grafana

# Check Loki metrics
curl http://localhost:3100/metrics
```

## 📚 INTEGRATION EXAMPLES

### **Sentry Integration:**
```python
# Correlate Sentry issues with logs
logger.log_backend_issue("A", sentry_event_id="abc123", 
                        error_message="RelevanceResult metadata")
```

### **Custom Metrics:**
```python
from prometheus_client import Counter, Histogram

# Custom metrics
COMMAND_COUNTER = Counter('hak_gal_commands_total', 'Total commands', ['command'])
QUERY_HISTOGRAM = Histogram('hak_gal_query_seconds', 'Query duration')

# Usage
COMMAND_COUNTER.labels(command='ask').inc()
with QUERY_HISTOGRAM.time():
    # Query processing
    pass
```

## 🚀 PRODUCTION DEPLOYMENT

### **Environment Variables:**
```bash
# .env file
LOKI_RETENTION_PERIOD=168h
GRAFANA_ADMIN_PASSWORD=your-secure-password
PROMETHEUS_RETENTION=30d
LOG_LEVEL=INFO
```

### **Resource Requirements:**
- **CPU:** 2-4 cores
- **Memory:** 4-8GB RAM
- **Storage:** 50-100GB SSD
- **Network:** 1Gbps

### **Backup Strategy:**
```bash
# Backup Grafana dashboards
curl -u admin:password http://localhost:3000/api/search?type=dash-db | \
  jq -r '.[].uid' | xargs -I {} curl -u admin:password \
  "http://localhost:3000/api/dashboards/uid/{}" > backup.json

# Backup Prometheus data
docker run --rm -v prometheus-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /data
```

## 📞 SUPPORT

### **Health Checks:**
```bash
# Service health
curl http://localhost:3100/ready      # Loki
curl http://localhost:9090/-/ready    # Prometheus
curl http://localhost:3000/api/health # Grafana

# HAK-GAL Backend health
curl http://localhost:5001/health     # Custom endpoint
```

### **Log Analysis:**
```bash
# Real-time error monitoring
tail -f observability/logs/api.log | jq 'select(.level=="ERROR")'

# Performance analysis
grep "query_time_ms" observability/logs/performance.log | \
  jq -r '.query_time_ms' | sort -n | tail -10
```

---

## ✨ FEATURES

✅ **Structured JSON Logging** - Loki-optimized format  
✅ **Real-time Dashboards** - Live HAK-GAL monitoring  
✅ **Proactive Alerting** - BACKEND-* issue detection  
✅ **Performance Tracking** - Query response times  
✅ **Error Correlation** - Sentry integration  
✅ **Automated Setup** - One-command deployment  
✅ **Production Ready** - Security & scalability  

**🎯 Result: MTTR reduction from hours to minutes!**
