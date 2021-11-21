import re
from copy import deepcopy
from collections import defaultdict
from enum import Enum
from rich import print as rprint

import ast

from deepdiff import diff

GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
END = '\033[0m'

class Unparser(ast._Unparser):
    def traverse(self, node):
        if isinstance(node, list):
            for item in node:
                self.traverse(item)
        else:
            colour = getattr(node, "colour", None)
            if colour is not None:
                self._source.append(colour)
            ast.NodeVisitor.visit(self, node)
            if colour is not None:
                self._source.append(END)

def split_path(path):
    parent, _, child = path.rpartition(".")
    m = re.match(r"(.*)\[(\d)]$", child)
    if m:
        prop = m.group(1)
        index = int(m.group(2))
    else:
        prop = child
        index = None

    return parent, prop, index

def print_diff(diff, now_path, then: ast.AST, now: ast.AST):
    print(f"diff --dast {now_path}")
    highlights = defaultdict(list)
    both = deepcopy(now)
    for change_type, changes in diff.items():
        for path, change in changes.items():
            parent_path, prop, index = split_path(path)
            parent = eval(parent_path.replace("root", "both"))
            description, is_added = describe_change(then, now, change_type, path)
            if isinstance(change, ast.AST):
                assert index is not None
                if is_added: # Only need to set node colour
                    getattr(parent, prop)[index].colour = GREEN
                else:
                    change.colour = RED
                    getattr(parent, prop).insert(index, change)
            else: # Changed
                change["old_value"].colour = RED
                change["new_value"].colour = GREEN
                if index is not None:
                    getattr(parent, prop).insert(index, change["old_value"])
                    getattr(parent, prop).insert(index, change["new_value"])
                else:
                    setattr(parent, prop, change["new_value"])
                    # TODO: Make old value

    unparser = Unparser()
    print(unparser.visit(both))


def unparse(maybe_node):
    if isinstance(maybe_node, ast.AST):
        return ast.unparse(maybe_node)
    else:
        return str(maybe_node)

def describe_node(node):
    if isinstance(node, ast.Module):
        return "module body"
    if isinstance(node, ast.ClassDef):
        return "class"
    if isinstance(node, ast.If):
        return f"if statement"
    if isinstance(node, ast.AugAssign):
        return f"augmented assignment"
    if isinstance(node, ast.Assign):
        return f"assignment"
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