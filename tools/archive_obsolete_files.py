# -*- coding: utf-8 -*-
#
# DATEI: archive_obsolete_files.py
# PROJEKT: HAK-GAL / ArchonOS
# VERSION: 1.1 (korrigierte und vollständige Dateiliste)
#
# BESCHREIBUNG:
# Dieses Werkzeug führt eine Konsolidierung des `tools`-Ordners durch.
# Es identifiziert veraltete oder durch neuere Versionen ersetzte Dateien,
# erstellt ein zeitgestempeltes ZIP-Archiv dieser Dateien im Backup-Verzeichnis
# und entfernt sie anschließend aus dem Quellverzeichnis.
#
# Diese Aktion erhöht die Wartbarkeit und Klarheit des Projekts, indem sie
# den Fokus auf den finalen, produktionsreifen Code-Stack legt.

import os
import zipfile
from pathlib import Path
from datetime import datetime

# --- KONFIGURATION ---

# 1. Definieren der Quell- und Zielverzeichnisse.
#    Pathlib wird für eine robuste, plattformunabhängige Pfadbehandlung verwendet.
SOURCE_DIR = Path("D:/MCP Mods/HAK_GAL_SUITE/tools")
BACKUP_DIR = Path("D:/Backups")

# 2. VOLLSTÄNDIGE Liste der zu archivierenden, veralteten Dateien.
#    Diese Liste basiert auf der finalen Analyse des Verzeichnisinhalts.
OBSOLETE_FILES = [
    # Ursprüngliche Liste der veralteten Dateien
    "belief_revision_test_report.py",
    "hak_gal_hyper_optimizer.py",
    "hak_gal_genesis_engine.py",
    "hak_gal_singularity_core.py",
    "hak_gal_orchestrator.py",
    "hak_gal_orchestrator3.py",
    "hak_gal_orchestrator4.py",
    "hak_gal_relevance_filter1.py",
    "archonos_blueprint_compiler.py",
    "archonos_blueprint_compiler_v2.py",
    "hak_gal_core_archon.py",
    "hak_gal_performance_profiler.py",
    "api.py",
    "schemas.py",
    
    # Neu identifizierte obsolete Dateien nach Verzeichnis-Analyse
    "ArchonOS_Integrated_Sandbox_Test1.py",
    "archonos_transcendence_engine.py",
    "archon_os_bootstrap.py",
    "hak_gal_belief_revision.py",
    "hak_gal_filter_integration.py",
]

def main():
    """Führt den Archivierungsprozess aus."""
    print("=" * 80)
    print("HAK-GAL / ArchonOS - Konsolidierungswerkzeug für veraltete Dateien")
    print("=" * 80)

    # --- Schritt 1: Validierung der Pfade ---
    if not SOURCE_DIR.is_dir():
        print(f"❌ FEHLER: Das Quellverzeichnis wurde nicht gefunden: {SOURCE_DIR}")
        return

    # Erstelle das Backup-Verzeichnis, falls es nicht existiert.
    # `exist_ok=True` verhindert einen Fehler, wenn der Ordner bereits da ist.
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"ℹ️ Quellverzeichnis: {SOURCE_DIR}")
        print(f"ℹ️ Backup-Verzeichnis: {BACKUP_DIR}")
    except OSError as e:
        print(f"❌ FEHLER: Konnte das Backup-Verzeichnis nicht erstellen: {e}")
        return

    # --- Schritt 2: Vorbereitung des Archivs ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_name = f"HAK_GAL_OBSOLETE_archive_{timestamp}.zip"
    archive_path = BACKUP_DIR / archive_name

    archived_files_count = 0
    skipped_files = []

    print(f"\n▶️ Starte Archivierungsprozess. Ziel-Archiv: {archive_path}\n")

    # --- Schritt 3: Archivierung und Bereinigung ---
    try:
        # Der `with`-Block stellt sicher, dass die ZIP-Datei korrekt geschlossen wird.
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in OBSOLETE_FILES:
                source_file_path = SOURCE_DIR / filename

                if source_file_path.is_file():
                    # Datei zum ZIP-Archiv hinzufügen.
                    # `arcname` stellt sicher, dass keine Verzeichnisstruktur im ZIP gespeichert wird.
                    zipf.write(source_file_path, arcname=filename)
                    print(f"  [ARCHIVIERT] {filename}")

                    # Originaldatei löschen.
                    os.remove(source_file_path)
                    print(f"  [GELÖSCHT]   {filename}")
                    archived_files_count += 1
                else:
                    # Datei wurde nicht gefunden, wahrscheinlich schon gelöscht.
                    skipped_files.append(filename)
                    print(f"  [ÜBERSPRUNGEN] {filename} (nicht gefunden)")

    except Exception as e:
        print(f"\n❌ Ein unerwarteter Fehler ist während der Archivierung aufgetreten: {e}")
        print("Der Prozess wurde abgebrochen. Möglicherweise ist das Archiv unvollständig.")
        return

    # --- Schritt 4: Zusammenfassung ---
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("-" * 80)
    print(f"Archivierungsprozess abgeschlossen.")
    print(f"✅ {archived_files_count} Dateien wurden erfolgreich archiviert und entfernt.")
    if skipped_files:
        print(f"🟡 {len(skipped_files)} Dateien wurden übersprungen, da sie nicht gefunden wurden:")
        for file in skipped_files:
            print(f"   - {file}")
    print(f"\nDas Backup-Archiv wurde erstellt unter:")
    print(f"   {archive_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()