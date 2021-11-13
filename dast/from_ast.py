import ast

def strip(node):
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
            else:
                pass