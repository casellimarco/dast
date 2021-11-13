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


def strip(node: ast.AST):
    """
    Remove certain properties of an AST that
    are not relevant for Python at runtime.
    """
    ignored_props = {"type_ignores", "type_coment", "col_offset", "end_col_offset", "lineno", "end_lineno"}
    for key, value in vars(node).copy().items():
        if key in ignored_props:
            delattr(node, key)
        else:
            if isinstance(value, list):
                for element in value:
                    strip(element)
            elif isinstance(value, ast.AST):
                strip(value)
