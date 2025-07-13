"""
HAK-GAL Advanced Tools Integration
==================================

Schritt-für-Schritt Integration des Orchestrator V5 als Drop-in-Replacement
für bestehende Filter-Systeme im HAK-GAL Backend.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util

class AdvancedToolsIntegration:
    """Integration Bridge für Advanced Tools"""
    
    def __init__(self):
        self.tools_path = Path(__file__).parent.parent.parent / "tools"  # Korrigierter Pfad
        self.dependencies_checked = False
        self.orchestrator_v5 = None
        self.fallback_mode = True
        
        # Store imported classes for later use
        self.OrchestratingRelevanceManager = None
        self.OrchestratorConfig = None
        self.FilterStrategy = None
        
    def check_dependencies(self) -> Dict[str, bool]:
        """Prüft alle Dependencies für Advanced Tools"""
        required_packages = {
            'sentence_transformers': False,
            'prometheus_client': False, 
            'cachetools': False,
            'sklearn': False,
            'numpy': False,
            'asyncio': True,  # Built-in
        }
        
        for package, status in required_packages.items():
            if package == 'asyncio':
                continue  # Built-in
            try:
                importlib.import_module(package)
                required_packages[package] = True
                print(f"✅ {package} verfügbar")
            except ImportError:
                print(f"❌ {package} fehlt")
        
        self.dependencies_checked = True
        return required_packages
    
    def install_missing_dependencies(self) -> bool:
        """Installiert fehlende Dependencies"""
        missing_packages = [
            'sentence-transformers',
            'prometheus-client',
            'cachetools', 
            'scikit-learn'
        ]
        
        try:
            import subprocess
            cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages
            print(f"🔧 Installiere: {' '.join(missing_packages)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies erfolgreich installiert")
                return True
            else:
                print(f"❌ Installation fehlgeschlagen: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Fehler bei Installation: {e}")
            return False
    
    def load_orchestrator_v5(self) -> bool:
        """Lädt Orchestrator V5 dynamisch"""
        try:
            print(f"🛠️ Debug: tools_path = {self.tools_path}")
            print(f"🛠️ Debug: tools_path exists = {self.tools_path.exists()}")
            
            # WICHTIG: sys.path VOR dem dynamischen Import setzen
            sys.path.insert(0, str(self.tools_path))
            print(f"✅ Tools-Pfad zu sys.path hinzugefügt: {self.tools_path}")
            
            # Import from tools directory explicitly 
            import importlib.util
            orchestrator_path = self.tools_path / 'hak_gal_orchestrator5.py'
            
            print(f"🛠️ Debug: orchestrator_path = {orchestrator_path}")
            print(f"🛠️ Debug: orchestrator_path exists = {orchestrator_path.exists()}")
            
            if not orchestrator_path.exists():
                print(f"❌ Orchestrator nicht gefunden: {orchestrator_path}")
                return False
            
            print(f"ℹ️ Lade Orchestrator aus: {orchestrator_path}")
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location("orchestrator_v5", orchestrator_path)
            orchestrator_module = importlib.util.module_from_spec(spec)
            
            # Execute module (jetzt sollten alle Imports funktionieren)
            spec.loader.exec_module(orchestrator_module)
            
            # Get classes from loaded module
            self.OrchestratingRelevanceManager = orchestrator_module.OrchestratingRelevanceManager
            self.OrchestratorConfig = orchestrator_module.OrchestratorConfig
            self.FilterStrategy = orchestrator_module.FilterStrategy
            
            print("✅ Orchestrator-Klassen erfolgreich geladen")
            
            # Import required data structures
            from hak_gal_relevance_filter import Fact, RelevanceResult
            
            # Initialize with safe config
            config = self.OrchestratorConfig(
                enable_semantic=False,  # Start conservative
                enable_learning=False,
                enable_distributed=False,
                enable_ml=False,
                enable_neuro_symbolic=False,
                structural_weight=1.0,  # Only structural initially
                max_query_time=1.0,
                min_confidence_score=0.1
            )
            
            self.orchestrator_v5 = self.OrchestratingRelevanceManager(config)
            self.fallback_mode = False
            print("✅ Orchestrator V5 erfolgreich geladen (Conservative Mode)")
            return True
            
        except ImportError as e:
            print(f"❌ Import-Fehler: {e}")
            return False
        except Exception as e:
            print(f"❌ Orchestrator V5 Initialisierung fehlgeschlagen: {e}")
            return False
    
    def enable_advanced_features(self) -> bool:
        """Aktiviert erweiterte Features schrittweise"""
        if not self.orchestrator_v5 or not self.OrchestratorConfig:
            print("❌ Orchestrator oder Config-Klasse nicht verfügbar")
            return False
        
        try:
            # Update config to enable more features
            new_config = self.OrchestratorConfig(
                enable_semantic=True,
                enable_learning=True,
                enable_distributed=False,  # Still disabled
                enable_ml=True,
                enable_neuro_symbolic=False,  # Still disabled
                structural_weight=0.25,
                semantic_weight=0.35,
                learned_weight=0.20,
                ml_weight=0.20,
                max_query_time=2.0,
                min_confidence_score=0.05
            )
            
            # Reinitialize with advanced config
            self.orchestrator_v5 = self.OrchestratingRelevanceManager(new_config)
            print("✅ Advanced Features aktiviert (Semantic + ML + Learning)")
            return True
            
        except Exception as e:
            print(f"❌ Advanced Features konnten nicht aktiviert werden: {e}")
            return False
    
    def get_orchestrator(self):
        """Gibt Orchestrator zurück oder None falls Fallback"""
        return self.orchestrator_v5 if not self.fallback_mode else None

# Singleton instance
_integration = AdvancedToolsIntegration()

def get_integration() -> AdvancedToolsIntegration:
    """Gibt Integration-Instance zurück"""
    return _integration

def bootstrap_advanced_tools() -> bool:
    """Bootstrap-Funktion für Advanced Tools"""
    integration = get_integration()
    
    print("🚀 HAK-GAL Advanced Tools Bootstrap...")
    
    # 1. Check dependencies
    deps = integration.check_dependencies()
    missing = [k for k, v in deps.items() if not v]
    
    if missing:
        print(f"⚠️ Fehlende Dependencies: {missing}")
        if input("Installieren? (j/n): ").lower() == 'j':
            if not integration.install_missing_dependencies():
                print("❌ Bootstrap fehlgeschlagen - Dependencies")
                return False
    
    # 2. Load Orchestrator V5
    if not integration.load_orchestrator_v5():
        print("❌ Bootstrap fehlgeschlagen - Orchestrator V5")
        return False
    
    # 3. Try advanced features
    if integration.enable_advanced_features():
        print("✅ Bootstrap erfolgreich - Full Advanced Mode")
    else:
        print("⚠️ Bootstrap teilweise erfolgreich - Conservative Mode")
    
    return True

if __name__ == "__main__":
    bootstrap_advanced_tools()
