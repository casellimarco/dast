"""
Module with utilities for transforming ASTs
"""
import ast
from typing import cast

from dast.pprint import PrettyAST

def prettify(node: ast.AST):
    """
    Turn an AST into a PrettyAST recursively
    """
    for child in ast.walk(node):
        node_type = child.__class__
        child.__class__ = PrettyAST
        child = cast(PrettyAST, child)
        child.node_type = node_type
