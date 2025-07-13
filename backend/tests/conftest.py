# -*- coding: utf-8 -*-
"""
Pytest Konfiguration für HAK-GAL Backend
"""

import sys
import os

# Füge sowohl das Projekt-Root als auch das Backend-Verzeichnis zum Python-Path hinzu
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(project_root, 'backend')

# Stelle sicher, dass beide Pfade im sys.path sind
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Debug-Ausgabe
print(f"[conftest.py] Python-Path konfiguriert:")
print(f"  - Project Root: {project_root}")
print(f"  - Backend Dir: {backend_dir}")
