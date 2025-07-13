# -*- coding: utf-8 -*-
"""
Erstellt einen Kompatibilitäts-Wrapper für die alte Monolith-Datei
"""

import os
import shutil


def create_compatibility_wrapper():
    """Erstellt einen Wrapper für Rückwärts-Kompatibilität."""
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    old_file = os.path.join(backend_dir, "k_assistant_main_v7_wolfram.py")
    
    wrapper_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kompatibilitäts-Wrapper für die alte Monolith-Struktur
Leitet alle Aufrufe an die neue modulare Struktur weiter
"""

import sys
import os

# Warnung ausgeben
print("=" * 70)
print("⚠️  WARNUNG: Sie verwenden die alte Monolith-Datei!")
print("    Die Anwendung wurde in eine modulare Struktur migriert.")
print("    Bitte verwenden Sie stattdessen: python backend/main.py")
print("=" * 70)
print()
print("Starte trotzdem mit neuer Struktur...")
print()

# Importiere und starte die neue main.py
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(backend_dir))
sys.path.insert(0, backend_dir)

from main import main_loop

if __name__ == "__main__":
    main_loop()
'''
    
    # Sichere die alte Datei falls sie noch original ist
    if os.path.exists(old_file):
        # Prüfe ob es schon ein Backup gibt
        backup_file = old_file.replace(".py", "_ORIGINAL.py.bak")
        if not os.path.exists(backup_file):
            # Prüfe Dateigröße - wenn > 50KB, dann ist es wahrscheinlich das Original
            if os.path.getsize(old_file) > 50000:
                shutil.copy2(old_file, backup_file)
                print(f"✅ Original-Monolith gesichert als: {os.path.basename(backup_file)}")
    
    # Erstelle Wrapper
    with open(old_file, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print(f"✅ Kompatibilitäts-Wrapper erstellt: {os.path.basename(old_file)}")
    
    # Erstelle auch Wrapper für andere alte Dateien
    other_old_files = [
        "k_assistant_main.py",
        "k_assistant_mainx.py"
    ]
    
    for old_file_name in other_old_files:
        old_path = os.path.join(backend_dir, old_file_name)
        if os.path.exists(old_path) and os.path.getsize(old_path) > 50000:
            # Sichere Original
            backup_path = old_path.replace(".py", "_ORIGINAL.py.bak")
            if not os.path.exists(backup_path):
                shutil.copy2(old_path, backup_path)
            
            # Erstelle Wrapper
            with open(old_path, 'w', encoding='utf-8') as f:
                f.write(wrapper_content)
            
            print(f"✅ Wrapper erstellt: {old_file_name}")


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("HAK-GAL - Erstelle Kompatibilitäts-Wrapper")
    print("=" * 60)
    print()
    
    create_compatibility_wrapper()
    
    print()
    print("✅ Fertig! Alte Aufrufe werden jetzt zur neuen Struktur umgeleitet.")
    print()
    print("Empfehlung: Verwenden Sie ab jetzt:")
    print("  python backend/main.py")


if __name__ == "__main__":
    main()
