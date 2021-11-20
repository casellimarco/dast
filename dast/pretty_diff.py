from enum import Enum

import ast

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_diff(diff, now_path, then, now):
    then_lines = ast.unparse(then)
    now_lines = ast.unparse(now)
    print(f"diff --git a/{now_path} b/{now_path}")
    print(f"--- a/{now_path}")
    print(f"+++ b/{now_path}")
    for change_type, changes in diff.items():
        for path, change in changes.items():
            description, is_added = describe_change(then, now, change_type, path)
            print(f"{Colors.CYAN}@@ -{0},{0} +{0},{0} @@{Colors.END} {description}")
            if isinstance(change, ast.AST):
                print_change_with_colour(change, is_added)
            else:
                print_change_with_colour(change['old_value'], False)
                print_change_with_colour(change['new_value'], True)


def print_change_with_colour(change, is_added):
    colour = Colors.GREEN if is_added else Colors.RED
    symbol = "+" if is_added else "-"
    change_text = symbol + unparse(change).replace("\n", "\n" + symbol)
    print(colour + change_text + Colors.END)


def unparse(maybe_node):
    if isinstance(maybe_node, ast.AST):
        return ast.unparse(maybe_node)
    else:
        return str(maybe_node)

def describe_node(node):
    if isinstance(node, ast.Module):
        return "module body"
    if isinstance(node, ast.If):
        return f"if statement"
    if isinstance(node, ast.AugAssign):
        return f"augmented assignment"
    if isinstance(node, ast.Call):
        return f"call to function {ast.unparse(node.func)}"
    if isinstance(node, ast.keyword):
        return "keyword"
    if isinstance(node, ast.Name):
        return "variable"
    if isinstance(node, ast.For):
        return "for loop"
    if isinstance(node, ast.FunctionDef):
        return f"function definition '{node.name}'"

    return str(node.__class__)

def describe_change(then, now, change_type, path):
    msg = ""

    is_added = True
    parent = describe_node(eval(path.replace("root", "then").rpartition(".")[0]))
    if change_type == "iterable_item_removed":
        node = describe_node(eval(path.replace("root", "then")))
        msg += f"{node} removed from {parent}"
        is_added = False
    elif change_type in ["type_changes", "values_changed"]:
        node = describe_node(eval(path.replace("root", "then")))
        msg += f"{node} changed in {parent}"
    elif change_type == "iterable_item_added":
        node = describe_node(eval(path.replace("root", "now")))
        msg += f"{node} added to {parent}"
        is_added = True
    else:
        return change_type + " unknown", None

    return msg, is_added