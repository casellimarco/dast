"""
Logic for printing diffs output by DeepDiff
"""
import ast
import re
from dataclasses import dataclass
from copy import deepcopy
from typing import Any, Optional, Tuple


GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
END = '\033[0m'

@dataclass
class Delta:
    """
    Node used to represent a change. Added to
    an AST and represented with arrows by `Unparser`
    """
    old: ast.AST
    new: ast.AST

@dataclass
class Wrapper:
    """
    Node used to assign colour to a simple string or int value
    """
    value: Any

class Unparser(ast._Unparser):  # type: ignore[name-defined]
    """
    Specialisation of Unparser visitor with the added
    ability to use colour to display diffs
    """
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

    def visit_Delta(self, node):  # pylint: disable=invalid-name
        """
        Add arrows to the source code to represent changes.
        """
        before_old = len("".join(self._source).splitlines())
        self.traverse(node.old)
        after_old = len("".join(self._source).splitlines())
        if after_old == before_old:
            self._source.append(YELLOW + "->" + END)
        else:
            self._source.append("\n" + YELLOW + "\N{Downwards Arrow}" * 3)
        self.traverse(node.new)

    def visit_Wrapper(self, node):  # pylint: disable=invalid-name
        """
        Do nothing - just keep going to the level below
        """
        self.traverse(node.value)

def split_path(path: str) -> Tuple[str, str, Optional[int]]:
    """
    Split an AST path into the parent and the sub-path
    to the child. For paths to iterables also produce the index

    >>> split_path("a.b.c")
    ('a.b', 'c', None)
    >>> split_path("a.b.c[5]")
    ('a.b', 'c', 5)
    >>> split_path("root.body[10]")
    ('root', 'body', 10)
    """
    parent, _, child = path.rpartition(".")
    match = re.match(r"(.*)\[(\d+)]$", child)
    index: Optional[int]
    if match:
        prop = match.group(1)
        index = int(match.group(2))
    else:
        prop = child
        index = None

    return parent, prop, index

def print_diff(diff, now_path, then: ast.AST, now: ast.AST):
    """
    Print the diff output by DeepDiff in a human-readable way.
    """
    print(f"diff --dast {now_path}")
    both = deepcopy(now)
    all_changes = []
    for change_type, changes in diff.items():
        for path, change in changes.items():
            description, is_added = describe_change(then, now, change_type, path)
            parent_path, prop, index = split_path(path)
            all_changes.append((index, parent_path, prop, change, description, is_added, path))

    for (
            index,
            parent_path,
            prop,
            change,
            description,
            is_added,
            path,
            ) in sorted(all_changes, key=lambda x: x[0] if x[0] is not None else -1):
        parent = eval(parent_path.replace("root", "both"))
        if isinstance(change, ast.AST):
            assert index is not None
            if is_added: # Only need to set node colour
                getattr(parent, prop)[index].colour = GREEN
            else:
                change.colour = RED  # type: ignore[attr-defined]
                getattr(parent, prop).insert(index, change)
        else: # Changed
            if prop in ["id", "name"]:
                setattr(parent, prop, RED + change["old_value"] + YELLOW + "->" + GREEN + change["new_value"] + END)
                continue
            if not isinstance(change["old_value"], ast.AST):
                change["old_value"] = Wrapper(change["old_value"])
                change["new_value"] = Wrapper(change["new_value"]) # Both must be simple types (string, int, etc.)
            change["old_value"].colour = RED
            change["new_value"].colour = GREEN
            print(prop)
            delta = Delta(change["old_value"], change["new_value"])
            if index is not None:
                getattr(parent, prop)[index] = delta
            else:
                setattr(parent, prop, delta)

    unparser = Unparser()
    print(unparser.visit(both))


def describe_node(node: ast.AST) -> str:
    """
    A generic description of a node in the AST
    """
    if isinstance(node, ast.Module):
        return "module body"
    if isinstance(node, ast.ClassDef):
        return "class"
    if isinstance(node, ast.If):
        return "if statement"
    if isinstance(node, ast.AugAssign):
        return "augmented assignment"
    if isinstance(node, ast.Assign):
        return "assignment"
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

def describe_change(then, now, change_type, path):  # pylint: disable=unused-argument
    """
    Describe a change based on the change type and the before/after
    """
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
