"""
The main script to be run by git diff.
To use this with git difftool put these lines in your
~/.gitconfig:

```
[difftool "dast"]
        cmd = "python3 -m dast $LOCAL $REMOTE"
[difftool]
        prompt = false
```
You can then run it with `git difftool -t dast`
"""
import ast
import sys
from functools import partial

from deepdiff import DeepDiff

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


_open_utf = partial(open, encoding="utf-8")

def main(then_path: str, now_path: str, verbose: bool = True):
    """
    Compare two python paths and print the difference
    """
    if not now_path.endswith(".py"):
        return None, None
    with _open_utf(then_path) as f_then:
        then_ast = ast.parse(f_then.read())

    with _open_utf(now_path) as f_now:
        now_ast = ast.parse(f_now.read())

    # This also includes end_lineno and end_col_offset
    ignored_props = {"type_ignores", "type_comment", "col_offset", "lineno"}
    callback = lambda _, path: any(path.endswith(prop) for prop in ignored_props)
    diff = DeepDiff(then_ast, now_ast, ignore_order=True, exclude_obj_callback=callback)
    if diff and verbose:
        print_diff(diff, now_path, then_ast, now_ast)

    return now_ast, then_ast, diff

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
        msg += f"Item changed in {parent}"
    elif change_type == "iterable_item_added":
        node = describe_node(eval(path.replace("root", "now")))
        msg += f"{node} added to {parent}"
        is_added = True
    else:
        return change_type + " unknown", None

    return msg, is_added


def print_diff(diff, now_path, then, now):
    print(f"diff --git a/{now_path} b/{now_path}")
    print(f"--- a/{now_path}")
    print(f"+++ b/{now_path}")
    for change_type, changes in diff.items():
        for path, change in changes.items():
            description, is_added = describe_change(then, now, change_type, path)
            print(f"{bcolors.OKCYAN}@@ -{0},{0} +{0},{0} @@{bcolors.ENDC} {description}")
            if isinstance(change, ast.AST):
                colour = bcolors.OKGREEN if is_added else bcolors.WARNING
                print(colour + ast.unparse(change) + bcolors.ENDC)
            else:
                print(f"{bcolors.WARNING}-{unparse(change['old_value'])}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}+{unparse(change['new_value'])}{bcolors.ENDC}")

def unparse(maybe_node):
    if isinstance(maybe_node, ast.AST):
        return ast.unparse(maybe_node)
    else:
        return str(maybe_node)

if __name__ == "__main__":
    now, then, diff = main(sys.argv[1], sys.argv[2])
