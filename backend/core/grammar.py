# -*- coding: utf-8 -*-
"""
HAK-GAL Grammatik-Definition
"""

HAKGAL_GRAMMAR = r"""
    ?start: formula
    formula: expression "."
    ?expression: quantified_formula | implication
    ?implication: disjunction ( "->" implication )?
    ?disjunction: conjunction ( "|" disjunction )?
    ?conjunction: negation ( "&" conjunction )?
    ?negation: "-" atom_expression | atom_expression
    ?atom_expression: atom | "(" expression ")"
    quantified_formula: "all" VAR "(" expression ")"
    atom: PREDICATE ("(" [arg_list] ")")?
    arg_list: term ("," term)*
    ?term: PREDICATE | VAR | NUMBER
    PREDICATE: /[A-ZÄÖÜ][a-zA-ZÄÖÜäöüß0-9_-]*/
    VAR: /[a-z][a-zA-Z0-9_]*/
    NUMBER: /[0-9]+([_][0-9]+)*/
    %import common.WS
    %ignore WS
"""
