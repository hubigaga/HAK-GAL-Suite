# SENTRY INTEGRATION - COMMIT & TEST

## 🚀 SCHRITT 1: ÄNDERUNGEN COMMITTEN

```powershell
# Sentry Integration zu Git hinzufügen
git add .env api.py test_sentry_integration.py

# Commit mit detaillierter Message
git commit -m "🛡️ SENTRY INTEGRATION: Live Error Tracking & Performance Monitoring

✅ IMPLEMENTIERTE FEATURES:
- Complete Sentry SDK Integration in api.py
- Error Tracking mit Context & Tags
- Performance Monitoring für alle Commands  
- Timeout Tracking & Custom Metrics
- Environment Configuration (.env)
- Comprehensive Test Script

🎯 MONITORING CAPABILITIES:
- Real-time Error Capture mit Stack Traces
- Command Performance Metrics
- Custom HAK-GAL Tags (prover_type, llm_provider)
- Transaction Tracking für alle API Calls
- Context-aware Error Reporting

📊 PRODUCTION FEATURES:
- Environment: production
- Release: 1.0.0-clean-architecture
- Traces Sample Rate: 100%
- Profiles Sample Rate: 100%

🧪 TESTING:
- Integration Test Script: test_sentry_integration.py
- Validates DSN, Error Tracking, Performance
- Backend Compatibility verified

Category: Production Monitoring"

# Push zu GitHub
git push origin main
```

## 🧪 SCHRITT 2: SENTRY INTEGRATION TESTEN

```powershell
# Test 1: Sentry Integration validieren
python test_sentry_integration.py

# Test 2: API Server mit Sentry starten
python api.py

# Test 3: Test Commands (in neuem Terminal/Browser)
# POST zu http://localhost:5001/api/command
# {"command": "ask Was ist Machine Learning?"}
```

## 📊 SCHRITT 3: SENTRY DASHBOARD ÜBERWACHEN

**Dashboard URLs:**
- Issues: https://samui-science-lab.sentry.io/issues/
- Performance: https://de.sentry.io/performance/
- Releases: https://de.sentry.io/releases/

**Erwartete Sentry Events:**
- ✅ Test Messages vom Integration Script
- ✅ Performance Transactions von API Calls
- ✅ Error Events bei Test-Exceptions
- ✅ Custom HAK-GAL Metrics

---

## 🎯 VALIDATION CHECKLIST

Nach den Tests sollten Sie sehen:

- [ ] **Sentry Dashboard zeigt Events** (Test Messages)
- [ ] **API läuft mit Sentry** (Startup Message)
- [ ] **Commands erzeugen Transactions** (Performance Tab)
- [ ] **Errors werden getrackt** (Issues Tab)
- [ ] **Custom Tags erscheinen** (component: hak-gal-api)

**Bei Problemen:** Prüfen Sie SENTRY_DSN in .env