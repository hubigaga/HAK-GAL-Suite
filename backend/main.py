# -*- coding: utf-8 -*-
"""
HAK-GAL SUITE Backend Main Application
Modularisierte Version mit Clean Architecture
"""

import os
import sys

# Füge das Projekt-Root zum Python-Path hinzu
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.services import KAssistant


def print_help():
    """Zeigt die Hilfe an."""
    print("\n" + " K-Assistant Hilfe (Archon-Prime mit Wolfram) ".center(70, "-"))
    print("  build_kb <pfad>      - Indiziert Dokument für RAG")
    print("  add_raw <formel>     - Fügt KERNREGEL hinzu")
    print("  retract <formel>     - Entfernt KERNREGEL")
    print("  learn                - Speichert gefundene Fakten")
    print("  show                 - Zeigt Wissensbasis an")
    print("  sources              - Zeigt Wissensquellen an")
    print("  search <anfrage>     - Findet Text in der KB (RAG)")
    print("  ask <frage>          - Beantwortet Frage (mit RAG + Wolfram)")
    print("  explain <frage>      - Erklärt eine Antwort")
    print("  ask_raw <formel>     - Stellt rohe logische Frage")
    print("  what_is <entity>     - Zeigt Profil einer Entität an")
    print("  status               - Zeigt Systemstatus und Portfolio-Metriken")
    print("  wolfram_stats        - Zeigt Wolfram|Alpha Cache-Statistiken")
    print("  add_oracle <pred>    - Fügt Oracle-Prädikat hinzu")
    print("  test_wolfram [query] - Testet Wolfram-Integration")
    print("  shell <befehl>       - Führt Shell-Befehl aus")
    print("  parse <formel>       - Testet Parser mit Formel")
    print("  clearcache           - Leert alle Caches")
    print("  exit                 - Beendet und speichert die KB")
    print("-" * 70 + "\n")


def show_in_console(assistant: KAssistant):
    """Zeigt die Wissensbasis in der Konsole an."""
    data = assistant.show()
    
    print("\n--- Permanente Wissensbasis (Kernregeln) ---")
    if not data['permanent_knowledge']:
        print("   (Leer)")
    else:
        for i, fact in enumerate(data['permanent_knowledge']):
            print(f"   [{i}] {fact}")
    
    if data['learnable_facts']:
        print("\n--- Vorgeschlagene Fakten (mit 'learn' übernehmen) ---")
        for i, fact in enumerate(data['learnable_facts']):
            print(f"   [{i}] {fact}")
    
    print("\n--- Indizierte Wissens-Chunks ---")
    stats = data['rag_stats']
    print(f"   (Dokumente: {stats['doc_count']}, Chunks: {stats['chunk_count']})")
    
    if not data['rag_chunks']:
        print("   (Leer oder RAG deaktiviert)")
    else:
        for chunk in data['rag_chunks'][:3]:
            print(f"   [{chunk['id']} from {chunk['source']}] {chunk['text_preview']}")
        if len(data['rag_chunks']) > 3:
            print(f"   ... und {len(data['rag_chunks']) - 3} weitere Chunks.")


def main_loop():
    """Hauptschleife der Anwendung."""
    try:
        # Lade Umgebungsvariablen
        try:
            from dotenv import load_dotenv
            if load_dotenv():
                print("✅ .env Datei geladen.")
        except ImportError:
            pass
        
        # Initialisiere Assistant
        assistant = KAssistant()
        print_help()
        
        # Command-Mapping
        command_map = {
            "exit": lambda a, args: a.save_kb(a.kb_filepath),
            "help": lambda a, args: print_help(),
            "build_kb": lambda a, args: a.build_kb_from_file(args),
            "add_raw": lambda a, args: a.add_raw(args),
            "retract": lambda a, args: a.retract(args),
            "learn": lambda a, args: a.learn_facts(),
            "clearcache": lambda a, args: a.clear_cache(),
            "ask": lambda a, args: a.ask(args),
            "explain": lambda a, args: a.explain(args),
            "ask_raw": lambda a, args: a.ask_raw(args),
            "status": lambda a, args: a.status(),
            "show": lambda a, args: show_in_console(a),
            "search": lambda a, args: a.search(args),
            "sources": lambda a, args: a.sources(),
            "what_is": lambda a, args: a.what_is(args),
            "shell": lambda a, args: a.execute_shell(args),
            "parse": lambda a, args: a.test_parser(args),
            # Wolfram-Befehle
            "wolfram_stats": lambda a, args: a.wolfram_stats(),
            "add_oracle": lambda a, args: a.add_oracle_predicate(args),
            "test_wolfram": lambda a, args: a.test_wolfram(args) if args else a.test_wolfram(),
        }
        
        no_args_commands = [
            "exit", "help", "learn", "clearcache", "status", 
            "show", "sources", "wolfram_stats"
        ]
        
        # Hauptschleife
        while True:
            try:
                user_input = input("k-assistant> ").strip()
                if not user_input:
                    continue
                
                # Parse Befehl
                parts = user_input.split(" ", 1)
                command = parts[0].lower()
                args = parts[1].strip('"\'') if len(parts) > 1 else ""
                
                # Führe Befehl aus
                if command in command_map:
                    if command in no_args_commands and args:
                        print(f"Befehl '{command}' erwartet keine Argumente.")
                    elif command not in no_args_commands and not args:
                        print(f"Befehl '{command}' benötigt ein Argument.")
                    else:
                        command_map[command](assistant, args)
                        if command == "exit":
                            break
                else:
                    print(f"Unbekannter Befehl: '{command}'. Geben Sie 'help' für Hilfe ein.")
                    
            except (KeyboardInterrupt, EOFError):
                print("\nBeende... Speichere Wissensbasis.")
                assistant.save_kb(assistant.kb_filepath)
                break
            except Exception as e:
                import traceback
                print(f"\n🚨 Unerwarteter Fehler: {e}")
                traceback.print_exc()
                
    except Exception as e:
        import traceback
        print(f"\n🚨 Kritischer Startfehler: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main_loop()
