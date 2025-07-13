# SENTRY INTEGRATION - IMPLEMENTATION GUIDE

## 🛡️ SENTRY SETUP FOR HAK-GAL SUITE

### 📊 **CREATED SENTRY PROJECTS:**

#### **Backend Project:**
- **Name:** HAK-GAL-Backend
- **Platform:** Python
- **DSN:** `https://48c80acd7769ef02cff4f1987071fd87@o4509639807205376.ingest.de.sentry.io/4509659832189008`
- **Organization:** samui-science-lab
- **Region:** https://de.sentry.io

### 🔧 **INTEGRATION STEPS:**

#### **1. Install Sentry SDK:**
```bash
pip install sentry-sdk[flask]
```

#### **2. Add to requirements.txt:**
```
sentry-sdk[flask]==1.40.0
```

#### **3. Update .env file:**
```bash
# Add to .env
SENTRY_DSN=https://48c80acd7769ef02cff4f1987071fd87@o4509639807205376.ingest.de.sentry.io/4509659832189008
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=1.0.0
```

#### **4. API Integration (api.py):**
```python
# Add at the top of api.py (after imports)
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import os

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        FlaskIntegration(
            auto_enabling_integrations=False,
            transaction_style='endpoint'
        ),
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
    release=os.getenv('SENTRY_RELEASE', 'unknown'),
    attach_stacktrace=True,
    send_default_pii=False
)

# Add custom context
sentry_sdk.set_tag("component", "hak-gal-api")
sentry_sdk.set_tag("system", "reasoning-engine")
```

#### **5. Backend Services Integration:**
```python
# Add to backend/services/k_assistant.py
import sentry_sdk

class KAssistant:
    def ask(self, question: str):
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("operation", "ask")
            scope.set_context("query", {"question": question[:100]})
            
            try:
                # Existing ask logic...
                pass
            except Exception as e:
                scope.set_extra("question_length", len(question))
                scope.set_level("error")
                sentry_sdk.capture_exception(e)
                raise
```

### 📊 **MONITORING CONFIGURATION:**

#### **Error Tracking:**
```python
# Custom error handling with context
def handle_command_error(command, error, context=None):
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("command_type", command)
        scope.set_level("error")
        
        if context:
            scope.set_context("command_context", context)
        
        sentry_sdk.capture_exception(error)
```

#### **Performance Monitoring:**
```python
# Performance tracking for critical operations
@sentry_sdk.trace
def benchmark_query_performance(query_func, *args, **kwargs):
    start_time = time.time()
    
    try:
        result = query_func(*args, **kwargs)
        
        # Track success metrics
        sentry_sdk.set_measurement("query_duration", time.time() - start_time)
        sentry_sdk.set_tag("query_status", "success")
        
        return result
    except Exception as e:
        sentry_sdk.set_measurement("query_duration", time.time() - start_time)
        sentry_sdk.set_tag("query_status", "failed")
        raise
```

### 🎯 **CUSTOM METRICS:**

```python
# Track HAK-GAL specific metrics
def track_reasoning_metrics(prover_type, success, duration):
    sentry_sdk.set_measurement(f"{prover_type}_duration", duration)
    sentry_sdk.set_tag(f"{prover_type}_success", success)
    
    # Custom event for reasoning analytics
    sentry_sdk.capture_message(
        f"Reasoning completed: {prover_type}",
        level="info",
        extras={
            "prover": prover_type,
            "success": success,
            "duration_ms": duration * 1000
        }
    )

# LLM Provider tracking
def track_llm_usage(provider, tokens_used, cost=None):
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("llm_provider", provider)
        scope.set_extra("tokens_used", tokens_used)
        if cost:
            scope.set_extra("estimated_cost", cost)
        
        sentry_sdk.capture_message(
            f"LLM Usage: {provider}",
            level="info"
        )
```

### 🚨 **ALERTS & DASHBOARDS:**

#### **Critical Alerts:**
- **API Error Rate** > 5%
- **Average Response Time** > 10 seconds
- **LLM Provider Failures** > 20%
- **Logic Engine Errors** > 10%

#### **Performance Dashboards:**
- **Query Performance by Type**
- **LLM Provider Response Times**
- **Cache Hit Rates**
- **Resource Usage Trends**

### 🔧 **TESTING SENTRY INTEGRATION:**

```python
# Test script: test_sentry_integration.py
import sentry_sdk

def test_sentry_error():
    """Test error capture"""
    try:
        raise Exception("Test error for Sentry integration")
    except Exception as e:
        sentry_sdk.capture_exception(e)

def test_sentry_message():
    """Test message capture"""
    sentry_sdk.capture_message("HAK-GAL Sentry integration test", level="info")

def test_sentry_performance():
    """Test performance monitoring"""
    with sentry_sdk.start_transaction(op="test", name="integration_test"):
        # Simulate work
        import time
        time.sleep(0.1)
        sentry_sdk.set_measurement("test_duration", 100)

if __name__ == "__main__":
    test_sentry_error()
    test_sentry_message()
    test_sentry_performance()
    print("✅ Sentry integration tests completed")
```

### 📋 **IMPLEMENTATION CHECKLIST:**

- [ ] **Install sentry-sdk package**
- [ ] **Add environment variables to .env**
- [ ] **Initialize Sentry in api.py**
- [ ] **Add error capturing to backend services**
- [ ] **Implement performance monitoring**
- [ ] **Configure custom metrics**
- [ ] **Set up alerts in Sentry dashboard**
- [ ] **Test integration with test script**
- [ ] **Monitor for 24 hours**
- [ ] **Optimize based on initial data**

---

> **🛡️ PRODUCTION-READY MONITORING**  
> **📊 Real-time Error Tracking & Performance Insights**  
> **🚀 Ready for Immediate Implementation**  
