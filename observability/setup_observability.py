#!/usr/bin/env python3
"""
HAK-GAL Observability Stack Setup
=================================

Automated setup script for Grafana Loki + Prometheus + Grafana observability stack.
Configures logging, monitoring, and alerting for HAK-GAL Backend.

Usage:
    python setup_observability.py [--quick] [--dev] [--production]
"""

import subprocess
import sys
import os
import time
import requests
import json
from pathlib import Path
from typing import List, Dict, Any

# Configuration
OBSERVABILITY_DIR = Path(__file__).parent
PROJECT_ROOT = OBSERVABILITY_DIR.parent
LOGS_DIR = OBSERVABILITY_DIR / "logs"
DATA_DIR = OBSERVABILITY_DIR / "data"

class ObservabilitySetup:
    """HAK-GAL Observability Stack Setup Manager"""
    
    def __init__(self, mode: str = "dev"):
        self.mode = mode
        self.compose_file = OBSERVABILITY_DIR / "docker-compose-loki.yml"
        self.services_status = {}
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        print("🔍 Checking prerequisites...")
        
        required_tools = ["docker", "docker-compose"]
        missing_tools = []
        
        for tool in required_tools:
            if subprocess.run(["which", tool], capture_output=True).returncode != 0:
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            print("Please install Docker and Docker Compose first.")
            return False
            
        print("✅ Prerequisites check passed")
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directories...")
        
        directories = [
            LOGS_DIR,
            DATA_DIR,
            DATA_DIR / "loki",
            DATA_DIR / "grafana", 
            DATA_DIR / "prometheus"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
    
    def setup_permissions(self):
        """Setup proper permissions for Docker volumes"""
        print("🔐 Setting up permissions...")
        
        # Set permissions for Grafana
        os.system(f"sudo chown -R 472:472 {DATA_DIR / 'grafana'}")
        
        # Set permissions for Loki
        os.system(f"sudo chown -R 10001:10001 {DATA_DIR / 'loki'}")
        
        print("✅ Permissions configured")
    
    def start_services(self):
        """Start observability services"""
        print("🚀 Starting observability services...")
        
        cmd = ["docker-compose", "-f", str(self.compose_file), "up", "-d"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to start services: {result.stderr}")
            return False
            
        print("✅ Services started successfully")
        return True
    
    def wait_for_services(self):
        """Wait for all services to be healthy"""
        print("⏳ Waiting for services to be ready...")
        
        services = {
            "Loki": "http://localhost:3100/ready",
            "Grafana": "http://localhost:3000/api/health",
            "Prometheus": "http://localhost:9090/-/ready"
        }
        
        max_retries = 30
        
        for service, url in services.items():
            print(f"  Checking {service}...")
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"  ✅ {service} is ready")
                        self.services_status[service] = "ready"
                        break
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"  ❌ {service} failed to start: {e}")
                        self.services_status[service] = "failed"
                    else:
                        time.sleep(2)
    
    def configure_grafana(self):
        """Configure Grafana dashboards and datasources"""
        print("📊 Configuring Grafana...")
        
        # Wait a bit more for Grafana to fully initialize
        time.sleep(5)
        
        grafana_url = "http://localhost:3000"
        auth = ("admin", "hak-gal-admin-2025")
        
        try:
            # Test authentication
            response = requests.get(f"{grafana_url}/api/org", auth=auth, timeout=10)
            if response.status_code == 200:
                print("✅ Grafana authentication successful")
            else:
                print(f"⚠️ Grafana authentication failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not configure Grafana: {e}")
            print("Manual configuration may be required.")
    
    def setup_hak_gal_logging(self):
        """Setup HAK-GAL Backend logging integration"""
        print("🔧 Setting up HAK-GAL logging integration...")
        
        # Check if backend directory exists
        backend_dir = PROJECT_ROOT / "backend"
        if not backend_dir.exists():
            print("⚠️ Backend directory not found, skipping logging integration")
            return
            
        # Create sample integration in api.py
        api_file = PROJECT_ROOT / "api.py"
        if api_file.exists():
            print("📝 Adding logging integration to api.py...")
            
            integration_code = '''
# HAK-GAL Observability Integration
try:
    from backend.logging_config import setup_hak_gal_logging
    hak_gal_logger = setup_hak_gal_logging(log_level="INFO")
    hak_gal_logger.info("HAK-GAL Backend started with observability")
except ImportError:
    print("⚠️ HAK-GAL logging not available - install logging dependencies")
    hak_gal_logger = None
'''
            
            with open(api_file, 'r') as f:
                content = f.read()
                
            if "hak_gal_logger" not in content:
                # Add integration at the top after imports
                lines = content.split('\n')
                insert_index = 0
                
                # Find last import line
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_index = i + 1
                
                lines.insert(insert_index, integration_code)
                
                with open(api_file, 'w') as f:
                    f.write('\n'.join(lines))
                    
                print("✅ Logging integration added to api.py")
            else:
                print("✅ Logging integration already present")
    
    def install_python_dependencies(self):
        """Install required Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        # Create requirements for observability
        observability_requirements = [
            "prometheus_client>=0.17.0",
            "python-json-logger>=2.0.0"
        ]
        
        for package in observability_requirements:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to install {package}: {e}")
    
    def run_validation_tests(self):
        """Run validation tests for the observability stack"""
        print("🧪 Running validation tests...")
        
        tests = [
            ("Loki API", "http://localhost:3100/loki/api/v1/label"),
            ("Prometheus API", "http://localhost:9090/api/v1/status/config"),
            ("Grafana API", "http://localhost:3000/api/health")
        ]
        
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {test_name} test passed")
                else:
                    print(f"⚠️ {test_name} test failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {test_name} test error: {e}")
    
    def generate_test_logs(self):
        """Generate test logs for validation"""
        print("📝 Generating test logs...")
        
        try:
            # Import and test logging
            sys.path.insert(0, str(PROJECT_ROOT))
            from backend.logging_config import setup_hak_gal_logging
            
            logger = setup_hak_gal_logging(log_level="DEBUG")
            
            # Generate various log types
            logger.info("HAK-GAL observability test started")
            logger.log_command("test_command", user_id="test_user", query_time_ms=123.45)
            logger.log_performance("test_operation", 567.89, memory_mb=64.5, cpu_percent=25.3)
            logger.warning("Test warning message")
            
            # Test backend issue logging
            logger.log_backend_issue("TEST", "Test backend issue for validation", 
                                   error_type="test", command="test")
            
            print("✅ Test logs generated successfully")
            
        except Exception as e:
            print(f"⚠️ Could not generate test logs: {e}")
    
    def print_summary(self):
        """Print setup summary and next steps"""
        print("\n" + "="*60)
        print("🎉 HAK-GAL OBSERVABILITY SETUP COMPLETE")
        print("="*60)
        
        print("\n📊 Service URLs:")
        print(f"  • Grafana:    http://localhost:3000 (admin/hak-gal-admin-2025)")
        print(f"  • Prometheus: http://localhost:9090")
        print(f"  • Loki:       http://localhost:3100")
        
        print("\n📋 Service Status:")
        for service, status in self.services_status.items():
            status_icon = "✅" if status == "ready" else "❌"
            print(f"  {status_icon} {service}: {status}")
        
        print("\n🔧 Next Steps:")
        print("  1. Open Grafana at http://localhost:3000")
        print("  2. Navigate to 'HAK-GAL Backend Monitoring' dashboard")
        print("  3. Run HAK-GAL Backend: python api.py")
        print("  4. Test commands in Frontend to see logs")
        print("  5. Check alerting rules in Prometheus")
        
        print("\n📁 Log Files:")
        print(f"  • API Logs:      {LOGS_DIR}/api.log")
        print(f"  • Performance:   {LOGS_DIR}/performance.log")
        print(f"  • Sentry:        {LOGS_DIR}/sentry.log")
        print(f"  • Advanced Tools: {LOGS_DIR}/advanced_tools.log")
        
        print("\n🚨 Troubleshooting:")
        print("  • Check Docker logs: docker-compose -f observability/docker-compose-loki.yml logs")
        print("  • Restart services: docker-compose -f observability/docker-compose-loki.yml restart")
        print("  • View HAK-GAL logs: tail -f observability/logs/api.log")
        
        print("\n✨ Happy Monitoring! ✨")


def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup HAK-GAL Observability Stack")
    parser.add_argument("--quick", action="store_true", help="Quick setup without validation")
    parser.add_argument("--dev", action="store_true", help="Development mode (default)")
    parser.add_argument("--production", action="store_true", help="Production mode")
    parser.add_argument("--skip-deps", action="store_true", help="Skip Python dependencies")
    
    args = parser.parse_args()
    
    mode = "production" if args.production else "dev"
    setup = ObservabilitySetup(mode=mode)
    
    print("🚀 HAK-GAL OBSERVABILITY SETUP")
    print("="*40)
    
    # Check prerequisites
    if not setup.check_prerequisites():
        return 1
    
    # Setup process
    setup.create_directories()
    
    if os.getuid() == 0 or sys.platform == "win32":  # Skip on Windows or if root
        print("⚠️ Skipping permission setup (Windows or root user)")
    else:
        setup.setup_permissions()
    
    # Install dependencies
    if not args.skip_deps:
        setup.install_python_dependencies()
    
    # Start services
    if not setup.start_services():
        return 1
    
    # Wait for services
    setup.wait_for_services()
    
    # Configure Grafana
    setup.configure_grafana()
    
    # Setup HAK-GAL integration
    setup.setup_hak_gal_logging()
    
    # Validation
    if not args.quick:
        setup.run_validation_tests()
        setup.generate_test_logs()
    
    # Summary
    setup.print_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
