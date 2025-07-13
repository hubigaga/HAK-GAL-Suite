# -*- coding: utf-8 -*-
"""
Shell-Integration für Systembefehle
"""

import subprocess
import platform
import os
from typing import Tuple, List


class ShellManager:
    """
    Verwaltet die Ausführung von Shell-Befehlen.
    Unterstützt verschiedene Shells auf verschiedenen Plattformen.
    """
    
    def __init__(self):
        """Initialisiert den Shell-Manager und erkennt die Umgebung."""
        self.system = platform.system()
        self.shell = self._detect_shell()
        print(f"🖥️ System: {self.system}, Shell: {self.shell}")
    
    def _detect_shell(self) -> str:
        """
        Erkennt die verfügbare Shell.
        
        Returns:
            Name der erkannten Shell
        """
        if self.system == "Windows":
            if os.path.exists(r"C:\Windows\System32\wsl.exe"):
                return "wsl"
            if os.path.exists(r"C:\Program Files\Git\bin\bash.exe"):
                return "git-bash"
            return "powershell"
        return "bash"
    
    def execute(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """
        Führt einen Shell-Befehl aus.
        
        Args:
            command: Der auszuführende Befehl
            timeout: Timeout in Sekunden
            
        Returns:
            Tuple aus:
            - bool: True bei Erfolg
            - str: Stdout-Ausgabe
            - str: Stderr-Ausgabe oder Fehlermeldung
        """
        try:
            if self.shell == "wsl":
                proc = subprocess.run(
                    ["wsl.exe", "bash", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8'
                )
            elif self.shell == "git-bash":
                proc = subprocess.run(
                    [r"C:\Program Files\Git\bin\bash.exe", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8'
                )
            elif self.shell == "powershell":
                proc = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8'
                )
            else:  # bash/sh
                proc = subprocess.run(
                    ["bash", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8'
                )
            
            return (proc.returncode == 0, proc.stdout, proc.stderr)
            
        except subprocess.TimeoutExpired:
            return (False, "", f"Timeout: Befehl überschritt {timeout}s")
        except Exception as e:
            return (False, "", f"Fehler: {e}")
    
    def analyze_system_facts(self) -> List[str]:
        """
        Analysiert das System und generiert logische Fakten.
        
        Returns:
            Liste von HAK-GAL Fakten über das System
        """
        facts = [
            f"LäuftAuf({self.system}).",
            f"VerwendetShell({self.shell}).",
            f"PythonVersion({platform.python_version().replace('.', '_')})."
        ]
        
        # Weitere System-Fakten könnten hier hinzugefügt werden
        # z.B. verfügbare Ressourcen, installierte Software etc.
        
        return facts
