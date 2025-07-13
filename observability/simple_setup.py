#!/usr/bin/env python3
"""
HAK-GAL Observability Stack - SIMPLE SETUP
==========================================
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, description=""):
    """Run command and show output"""
    print(f"\n🔧 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ SUCCESS: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
    else:
        print(f"❌ FAILED: {description}")
        print(f"Error: {result.stderr}")
        return False
    return True

def main():
    print("🚀 HAK-GAL OBSERVABILITY STACK - SIMPLE SETUP")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if docker-compose file exists
    compose_file = current_dir / "docker-compose-loki.yml"
    if not compose_file.exists():
        print(f"❌ File not found: {compose_file}")
        print("Please ensure you're in the observability directory")
        return 1
    
    print(f"✅ Found compose file: {compose_file}")
    
    # Create logs directory
    logs_dir = current_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Created logs directory: {logs_dir}")
    
    # Check Docker
    if not run_command(["docker", "--version"], "Checking Docker"):
        print("❌ Docker not available. Please install Docker first.")
        return 1
    
    if not run_command(["docker-compose", "--version"], "Checking Docker Compose"):
        print("❌ Docker Compose not available. Please install Docker Compose first.")
        return 1
    
    # Start services
    print(f"\n🚀 Starting HAK-GAL Observability Services...")
    cmd = ["docker-compose", "-f", "docker-compose-loki.yml", "up", "-d"]
    
    if not run_command(cmd, "Starting Docker services"):
        return 1
    
    # Show services
    print(f"\n📊 Checking running services...")
    run_command(["docker-compose", "-f", "docker-compose-loki.yml", "ps"], "Service status")
    
    # Wait and test services
    print(f"\n⏳ Waiting for services to start (30 seconds)...")
    time.sleep(30)
    
    # Test services
    services = [
        ("Loki", "http://localhost:3100/ready"),
        ("Grafana", "http://localhost:3000/api/health"),
        ("Prometheus", "http://localhost:9090/-/ready")
    ]
    
    print(f"\n🧪 Testing service endpoints...")
    
    try:
        import requests
        
        for service, url in services:
            try:
                print(f"  Testing {service}...")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {service} is ready")
                else:
                    print(f"  ⚠️ {service} returned HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ {service} test failed: {e}")
                
    except ImportError:
        print("⚠️ 'requests' module not available, skipping endpoint tests")
        print("Install with: pip install requests")
    
    # Print access information
    print(f"\n" + "=" * 60)
    print("🎉 HAK-GAL OBSERVABILITY SETUP COMPLETED")
    print("=" * 60)
    
    print(f"\n📊 Service URLs:")
    print(f"  🎯 Grafana:    http://localhost:3000")
    print(f"     Login:     admin / hak-gal-admin-2025")
    print(f"  📈 Prometheus: http://localhost:9090")
    print(f"  📜 Loki:       http://localhost:3100")
    
    print(f"\n🔧 Next Steps:")
    print(f"  1. Open Grafana: http://localhost:3000")
    print(f"  2. Login with: admin / hak-gal-admin-2025")
    print(f"  3. Go to Dashboards → Browse → HAK-GAL")
    print(f"  4. Start HAK-GAL Backend: python ../api.py")
    print(f"  5. Test commands in Frontend")
    
    print(f"\n📋 Troubleshooting:")
    print(f"  • Service logs: docker-compose -f docker-compose-loki.yml logs")
    print(f"  • Restart:      docker-compose -f docker-compose-loki.yml restart")
    print(f"  • Stop:         docker-compose -f docker-compose-loki.yml down")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    input(f"\nPress Enter to exit...")
    sys.exit(exit_code)
