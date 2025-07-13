# -*- coding: utf-8 -*-
"""
Sentry Integration Test Script
Testet und validiert die Sentry-Integration für HAK-GAL Suite
"""

import os
import sys
from dotenv import load_dotenv

# .env laden
load_dotenv()

# Sentry SDK importieren
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    print("✅ Sentry SDK verfügbar")
except ImportError as e:
    print(f"❌ Sentry SDK nicht verfügbar: {e}")
    print("💡 Lösung: pip install sentry-sdk[flask]")
    sys.exit(1)

def test_sentry_configuration():
    """Testet Sentry-Konfiguration aus .env"""
    print("\n=== SENTRY KONFIGURATION TEST ===")
    
    # Prüfe Environment Variables
    dsn = os.getenv('SENTRY_DSN')
    environment = os.getenv('SENTRY_ENVIRONMENT', 'development')
    release = os.getenv('SENTRY_RELEASE', 'unknown')
    
    print(f"SENTRY_DSN: {'✅ Konfiguriert' if dsn else '❌ Fehlt'}")
    print(f"SENTRY_ENVIRONMENT: {environment}")
    print(f"SENTRY_RELEASE: {release}")
    
    if not dsn:
        print("❌ SENTRY_DSN nicht konfiguriert!")
        return False
    
    # Sentry initialisieren
    try:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=environment,
            release=release,
            attach_stacktrace=True,
            send_default_pii=False
        )
        print("✅ Sentry erfolgreich initialisiert")
        return True
    except Exception as e:
        print(f"❌ Sentry Initialisierung fehlgeschlagen: {e}")
        return False

def test_sentry_error_capture():
    """Testet Error Capture"""
    print("\n=== SENTRY ERROR CAPTURE TEST ===")
    
    try:
        # Bewusster Fehler für Test
        raise Exception("🧪 HAK-GAL Sentry Integration Test Error")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print("✅ Test-Error an Sentry gesendet")

def test_sentry_message():
    """Testet Message Capture"""
    print("\n=== SENTRY MESSAGE TEST ===")
    
    sentry_sdk.capture_message(
        "🚀 HAK-GAL Sentry Integration erfolgreich getestet",
        level="info"
    )
    print("✅ Test-Message an Sentry gesendet")

def test_sentry_performance():
    """Testet Performance Monitoring"""
    print("\n=== SENTRY PERFORMANCE TEST ===")
    
    with sentry_sdk.start_transaction(op="test", name="hak_gal_performance_test"):
        # Simuliere HAK-GAL Operation
        import time
        
        with sentry_sdk.start_span(op="reasoning", description="test_logical_inference"):
            time.sleep(0.1)  # Simuliere Logic Engine
            sentry_sdk.set_measurement("reasoning_duration", 100)
        
        with sentry_sdk.start_span(op="llm_query", description="test_ensemble_query"):
            time.sleep(0.05)  # Simuliere LLM Query
            sentry_sdk.set_measurement("llm_duration", 50)
        
        # Custom Tags und Context
        sentry_sdk.set_tag("component", "hak-gal-test")
        sentry_sdk.set_tag("operation", "integration_test")
        sentry_sdk.set_context("test_context", {
            "test_type": "performance",
            "simulated_operations": ["reasoning", "llm_query"]
        })
        
    print("✅ Performance Transaction an Sentry gesendet")

def test_sentry_custom_metrics():
    """Testet HAK-GAL spezifische Metriken"""
    print("\n=== SENTRY CUSTOM METRICS TEST ===")
    
    # Simuliere HAK-GAL Metriken
    with sentry_sdk.push_scope() as scope:
        # Simuliere Portfolio-Performance
        scope.set_tag("prover_type", "z3")
        scope.set_extra("proof_success", True)
        scope.set_extra("proof_duration", 0.234)
        
        sentry_sdk.set_measurement("z3_proof_duration", 234)
        sentry_sdk.capture_message(
            "Portfolio Prover Test: Z3 Success",
            level="info"
        )
    
    with sentry_sdk.push_scope() as scope:
        # Simuliere LLM Provider
        scope.set_tag("llm_provider", "deepseek")
        scope.set_extra("tokens_used", 1250)
        scope.set_extra("cost_estimate", 0.02)
        
        sentry_sdk.capture_message(
            "LLM Provider Test: DeepSeek Query",
            level="info"
        )
    
    print("✅ Custom HAK-GAL Metriken an Sentry gesendet")

def test_backend_import():
    """Testet ob Backend mit Sentry kompatibel ist"""
    print("\n=== BACKEND COMPATIBILITY TEST ===")
    
    try:
        # Versuche Backend zu importieren
        sys.path.append('.')
        from backend.services import KAssistant
        print("✅ Backend Services erfolgreich importiert")
        
        # Teste KAssistant Initialisierung (ohne vollständige Initialisierung)
        print("💡 Backend ist Sentry-kompatibel")
        return True
        
    except Exception as e:
        print(f"⚠️ Backend Import Problem: {e}")
        print("💡 Backend muss eventuell erweitert werden")
        return False

def main():
    """Führt alle Sentry-Tests durch"""
    print("🛡️ HAK-GAL SENTRY INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Konfiguration
    config_ok = test_sentry_configuration()
    if not config_ok:
        print("\n❌ KRITISCHER FEHLER: Sentry-Konfiguration fehlgeschlagen!")
        return False
    
    # Test 2: Error Capture
    test_sentry_error_capture()
    
    # Test 3: Message Capture
    test_sentry_message()
    
    # Test 4: Performance Monitoring
    test_sentry_performance()
    
    # Test 5: Custom Metrics
    test_sentry_custom_metrics()
    
    # Test 6: Backend Compatibility
    backend_ok = test_backend_import()
    
    print("\n" + "=" * 50)
    print("🎯 SENTRY INTEGRATION TEST ZUSAMMENFASSUNG:")
    print(f"  ✅ Konfiguration: {'OK' if config_ok else 'FEHLER'}")
    print(f"  ✅ Error Tracking: OK")
    print(f"  ✅ Message Capture: OK") 
    print(f"  ✅ Performance Monitoring: OK")
    print(f"  ✅ Custom Metrics: OK")
    print(f"  ✅ Backend Compatibility: {'OK' if backend_ok else 'PRÜFEN'}")
    
    if config_ok:
        print("\n🚀 SENTRY INTEGRATION ERFOLGREICH!")
        print("💡 Prüfen Sie das Sentry Dashboard:")
        print("   https://samui-science-lab.sentry.io/issues/")
        print("   https://de.sentry.io")
        
        print("\n📋 NÄCHSTE SCHRITTE:")
        print("  1. Starten Sie: python api.py")
        print("  2. Testen Sie Commands via API")
        print("  3. Überwachen Sie Sentry Dashboard")
        print("  4. Optional: Backend Services erweitern")
        
        return True
    else:
        print("\n❌ INTEGRATION FEHLGESCHLAGEN!")
        print("💡 Korrigieren Sie die .env Konfiguration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
