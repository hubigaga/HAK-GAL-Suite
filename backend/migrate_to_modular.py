# -*- coding: utf-8 -*-
"""
Migrations-Skript: Monolith -> Modulare Architektur
Hilft beim Übergang von der alten zur neuen Struktur
"""

import os
import shutil
import sys


def migrate_to_modular():
    """Migriert von der monolithischen zur modularen Struktur."""
    print("🔄 Starte Migration zur modularen Architektur...")
    
    # Pfade
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    old_main = os.path.join(backend_dir, "k_assistant_main_v7_wolfram.py")
    
    # 1. Sichere alte Datei
    if os.path.exists(old_main):
        backup_name = old_main.replace(".py", "_BACKUP_MONOLITH.py")
        if not os.path.exists(backup_name):
            shutil.copy2(old_main, backup_name)
            print(f"✅ Backup erstellt: {backup_name}")
    
    # 2. Erstelle symbolischen Link oder Wrapper
    wrapper_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrapper für Kompatibilität mit alter Struktur
Leitet auf neue modulare Architektur um
"""

import sys
import os

# Importiere neue main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import main_loop

if __name__ == "__main__":
    print("⚠️  HINWEIS: Sie verwenden den alten Entry Point.")
    print("    Bitte wechseln Sie zu: python backend/main.py")
    print("    Starte trotzdem...\\n")
    main_loop()
'''
    
    wrapper_path = os.path.join(backend_dir, "k_assistant_main_v7_wolfram_wrapper.py")
    with open(wrapper_path, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    print(f"✅ Kompatibilitäts-Wrapper erstellt: {wrapper_path}")
    
    # 3. Aktualisiere Batch-Dateien
    batch_updates = {
        "../start_suite_webui.bat": {
            "old": "python backend/k_assistant_main_v7_wolfram.py",
            "new": "python backend/main.py"
        },
        "../start_system.bat": {
            "old": "python backend/k_assistant_main_v7_wolfram.py",
            "new": "python backend/main.py"
        }
    }
    
    for batch_file, replacements in batch_updates.items():
        batch_path = os.path.join(backend_dir, batch_file)
        if os.path.exists(batch_path):
            try:
                with open(batch_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if replacements["old"] in content:
                    new_content = content.replace(replacements["old"], replacements["new"])
                    
                    # Backup
                    backup_path = batch_path + ".backup"
                    if not os.path.exists(backup_path):
                        shutil.copy2(batch_path, backup_path)
                    
                    # Update
                    with open(batch_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"✅ Aktualisiert: {os.path.basename(batch_path)}")
            except Exception as e:
                print(f"⚠️  Fehler beim Aktualisieren von {batch_file}: {e}")
    
    # 4. Erstelle __init__.py Dateien falls fehlend
    init_files = [
        "core/__init__.py",
        "api/__init__.py", 
        "services/__init__.py",
        "adapters/__init__.py",
        "infrastructure/__init__.py",
        "adapters/provers/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = os.path.join(backend_dir, init_file)
        if not os.path.exists(init_path):
            os.makedirs(os.path.dirname(init_path), exist_ok=True)
            with open(init_path, 'w') as f:
                f.write("# -*- coding: utf-8 -*-\n")
            print(f"✅ Erstellt: {init_file}")
    
    print("\n✅ Migration abgeschlossen!")
    print("\n📋 Nächste Schritte:")
    print("1. Testen Sie die neue Struktur: python backend/main.py")
    print("2. Führen Sie die Tests aus: python backend/tests/test_core.py")
    print("3. Prüfen Sie die Batch-Dateien")
    print("4. Entfernen Sie nach erfolgreichen Tests die alten Dateien")


def verify_structure():
    """Verifiziert die neue Modulstruktur."""
    print("\n🔍 Verifiziere Modulstruktur...")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_structure = {
        "core": ["models.py", "grammar.py", "parser.py", "fol_core.py"],
        "api": ["base_provider.py", "base_prover.py", "base_cache.py"],
        "services": ["complexity_analyzer.py", "prover_portfolio_manager.py", 
                    "ensemble_manager.py", "wissensbasis_manager.py", "k_assistant.py"],
        "adapters": ["llm_providers.py"],
        "adapters/provers": ["functional_constraint.py", "pattern.py", 
                            "z3_adapter.py", "wolfram.py"],
        "infrastructure": ["caching.py", "persistence.py", "shell.py"],
        "tests": ["test_core.py"]
    }
    
    all_good = True
    
    for directory, files in required_structure.items():
        dir_path = os.path.join(backend_dir, directory)
        
        if not os.path.exists(dir_path):
            print(f"❌ Verzeichnis fehlt: {directory}")
            all_good = False
            continue
        
        for file in files:
            file_path = os.path.join(dir_path, file)
            if os.path.exists(file_path):
                print(f"✅ {directory}/{file}")
            else:
                print(f"❌ Datei fehlt: {directory}/{file}")
                all_good = False
    
    # Prüfe Hauptdateien
    for main_file in ["main.py", "README_ARCHITEKTUR.md"]:
        if os.path.exists(os.path.join(backend_dir, main_file)):
            print(f"✅ {main_file}")
        else:
            print(f"❌ {main_file} fehlt")
            all_good = False
    
    if all_good:
        print("\n✅ Alle Module vorhanden!")
    else:
        print("\n⚠️  Einige Module fehlen. Bitte prüfen.")
    
    return all_good


if __name__ == "__main__":
    print("HAK-GAL SUITE - Migration zur modularen Architektur")
    print("=" * 50)
    
    # Führe Migration durch
    migrate_to_modular()
    
    # Verifiziere Struktur
    if verify_structure():
        print("\n🎉 Migration erfolgreich abgeschlossen!")
    else:
        print("\n⚠️  Migration abgeschlossen, aber einige Dateien fehlen.")
        print("    Bitte prüfen Sie die Struktur manuell.")
