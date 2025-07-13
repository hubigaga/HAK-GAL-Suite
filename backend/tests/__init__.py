# -*- coding: utf-8 -*-
"""
Test-Suite für die HAK-GAL Backend-Module
"""

import sys
import os

# Konfiguriere Python-Path für Tests
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
