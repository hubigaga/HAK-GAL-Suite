# -*- coding: utf-8 -*-
"""
Z3 SMT Solver Adapter
"""

import re
from typing import Optional, Tuple, List, Dict, Any, Set

try:
    import z3
except ImportError:
    print("❌ FEHLER: 'z3-solver' nicht gefunden. Bitte mit 'pip install z3-solver' installieren.")
    z3 = None

from backend.api import BaseProver
from backend.core import HAKGALParser


class Z3Adapter(BaseProver):
    """
    Adapter für den Z3 SMT Solver.
    Übersetzt HAK-GAL Formeln in Z3-Ausdrücke und nutzt Z3 für Beweise.
    """
    
    def __init__(self):
        """Initialisiert den Z3 Adapter."""
        super().__init__("Z3 SMT Solver")
        if z3:
            z3.set_param('proof', True)
        self.parser = HAKGALParser()
        self.func_cache: Dict[Tuple[str, int], Any] = {}
    
    def prove(self, assumptions: List[str], goal: str) -> Tuple[Optional[bool], str]:
        """
        Beweist ein Ziel mit Z3.
        
        Übersetzt die Annahmen und das negierte Ziel in Z3-Constraints.
        Wenn Z3 UNSAT zurückgibt, ist das Ziel bewiesen.
        """
        if not z3:
            return None, "Z3 nicht verfügbar"
        
        solver = z3.Tactic('smt').solver()
        solver.set(model=True)
        self.func_cache = {}
        
        try:
            # Füge alle Annahmen hinzu
            for fact_str in assumptions:
                solver.add(self._parse_hakgal_formula_to_z3_expr(fact_str))
            
            # Füge negiertes Ziel hinzu
            goal_expr = self._parse_hakgal_formula_to_z3_expr(goal)
            solver.add(z3.Not(goal_expr))
            
        except (ValueError, z3.Z3Exception) as e:
            return (None, f"Fehler beim Parsen: {e}")
        
        # Prüfe Erfüllbarkeit
        check_result = solver.check()
        
        if check_result == z3.unsat:
            return (True, "Z3 hat das Ziel bewiesen.")
        elif check_result == z3.sat:
            return (False, f"Z3 konnte das Ziel nicht beweisen (Gegenmodell):\n{solver.model()}")
        else:
            return (None, f"Z3 konnte das Ziel nicht beweisen (Grund: {solver.reason_unknown()}).")
    
    def validate_syntax(self, formula: str) -> Tuple[bool, str]:
        """Validiert Syntax mit Parser und Z3-Konvertierung."""
        success, _, msg = self.parser.parse(formula)
        if not success:
            return (False, f"Parser: {msg}")
        
        if not z3:
            return (True, "✅ Syntax OK (Z3 nicht verfügbar)")
        
        try:
            self.func_cache = {}
            self._parse_hakgal_formula_to_z3_expr(formula)
            return (True, "✅ Syntax OK (Lark + Z3)")
        except (ValueError, z3.Z3Exception) as e:
            return (False, f"Z3-Konvertierung fehlgeschlagen: {e}")
    
    def _parse_hakgal_formula_to_z3_expr(self, formula_str: str, quantified_vars: Set[str] = None):
        """
        Konvertiert eine HAK-GAL Formel in einen Z3-Ausdruck.
        
        Args:
            formula_str: Die zu konvertierende Formel
            quantified_vars: Menge der quantifizierten Variablen
            
        Returns:
            Z3-Ausdruck
        """
        if quantified_vars is None:
            quantified_vars = set()
        
        formula_str = formula_str.strip().removesuffix('.')
        
        def _find_top_level_operator(s: str, operators: List[str]) -> Tuple[int, Optional[str]]:
            """Findet den obersten Operator in der Formel."""
            balance = 0
            for i in range(len(s) - 1, -1, -1):
                if s[i] == ')':
                    balance += 1
                elif s[i] == '(':
                    balance -= 1
                elif balance == 0:
                    for op in operators:
                        if s.startswith(op, i):
                            return i, op
            return -1, None
        
        expr = formula_str.strip()
        
        # Gleichheit
        if '=' in expr and not any(op in expr for op in ['->', '|', '&']):
            parts = expr.split('=')
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                # Verarbeite Zahlen mit Unterstrichen
                if re.match(r'^[0-9]+([_]?[0-9]+)*$', left):
                    left_z3 = z3.IntVal(int(left.replace('_', '')))
                elif left in quantified_vars:
                    left_z3 = z3.Int(left)
                else:
                    left_z3 = z3.Int(left)
                    
                if re.match(r'^[0-9]+([_]?[0-9]+)*$', right):
                    right_z3 = z3.IntVal(int(right.replace('_', '')))
                elif right in quantified_vars:
                    right_z3 = z3.Int(right)
                else:
                    right_z3 = z3.Int(right)
                    
                return left_z3 == right_z3
        
        # Logische Operatoren
        op_map = {'->': z3.Implies, '|': z3.Or, '&': z3.And}
        for op_str, op_func in op_map.items():
            idx, op = _find_top_level_operator(expr, [op_str])
            if idx != -1:
                left_expr = self._parse_hakgal_formula_to_z3_expr(expr[:idx], quantified_vars)
                right_expr = self._parse_hakgal_formula_to_z3_expr(expr[idx + len(op):], quantified_vars)
                return op_func(left_expr, right_expr)
        
        # Negation
        if expr.startswith('-'):
            return z3.Not(self._parse_hakgal_formula_to_z3_expr(expr[1:], quantified_vars))
        
        # Quantifikation
        if expr.startswith('all '):
            # Versuche zuerst das Standard-Format mit Klammern
            match = re.match(r"all\s+([\w]+)\s+\((.*)\)$", expr, re.DOTALL)
            if match:
                var_name, body = match.groups()
            else:
                # Alternative: Mehrere Quantoren hintereinander (alt)
                # z.B. "all x all y all z ..."
                # Konvertiere zu verschachteltem Format
                if re.match(r"all\s+\w+\s+all", expr):
                    # Extrahiere alle Quantoren
                    quantor_pattern = r"all\s+([\w]+)"
                    vars = re.findall(quantor_pattern, expr)
                    
                    # Finde den Körper (nach dem letzten "all var")
                    last_match = None
                    for match in re.finditer(quantor_pattern, expr):
                        last_match = match
                    
                    if last_match and vars:
                        body_start = last_match.end()
                        body = expr[body_start:].strip()
                        
                        # Baue verschachtelte Struktur von innen nach außen
                        result = body
                        for var in reversed(vars[1:]):
                            result = f"all {var} ({result})"
                        
                        # Verarbeite den äußersten Quantor normal
                        var_name = vars[0]
                        body = result
                    else:
                        raise ValueError(f"Konnte Quantoren nicht extrahieren aus: '{expr}'")
                else:
                    raise ValueError(f"Ungültiges Quantifikator-Format: '{expr}'")
            
            z3_var = z3.Int(var_name)
            body_expr = self._parse_hakgal_formula_to_z3_expr(body, quantified_vars | {var_name})
            return z3.ForAll([z3_var], body_expr)
        
        # Geklammerte Ausdrücke
        if expr.startswith('(') and expr.endswith(')'):
            return self._parse_hakgal_formula_to_z3_expr(expr[1:-1], quantified_vars)
        
        # Atomare Prädikate
        match = re.match(r"([A-ZÄÖÜ][\w]*)\s*\((.*?)\)", expr)
        if match:
            pred_name, args_str = match.groups()
            args = [a.strip() for a in args_str.split(',') if a.strip()]
            
            z3_args = []
            for arg in args:
                if arg in quantified_vars:
                    z3_args.append(z3.Int(arg))
                elif re.match(r'^[0-9]+([_]?[0-9]+)*$', arg):  # NUMBER pattern (mit optionalen Unterstrichen)
                    z3_args.append(z3.IntVal(int(arg.replace('_', ''))))
                else:
                    z3_args.append(z3.Int(arg))
            
            func_sig = (pred_name, len(z3_args))
            if func_sig not in self.func_cache:
                self.func_cache[func_sig] = z3.Function(
                    pred_name,
                    *([z3.IntSort()] * len(z3_args)),
                    z3.BoolSort()
                )
            return self.func_cache[func_sig](*z3_args)
        
        # Nullstellige Prädikate
        if re.match(r"^[A-ZÄÖÜ][\w]*$", expr):
            func_sig = (expr, 0)
            if func_sig not in self.func_cache:
                self.func_cache[func_sig] = z3.Function(expr, z3.BoolSort())
            return self.func_cache[func_sig]()
        
        raise ValueError(f"Konnte Formelteil nicht parsen: '{expr}'")
