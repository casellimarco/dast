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

from dast.pretty_diff import print_diff

def match_pairs(x, y, _):
    """
    Compare two objects and return True if they are identical. Can be extended
    to matching non-identical objects by setting a distance threshold
    """
    minidiff = DeepDiff(x, y, exclude_obj_callback=callback, iterable_compare_func=match_pairs, get_deep_distance=True)
    distance = minidiff.tree["deep_distance"]

    return distance == []

# This also includes end_lineno and end_col_offset
ignored_props = {"col_offset", "lineno"}
callback = lambda _, path: any(path.endswith(prop) for prop in ignored_props)

_open_utf = partial(open, encoding="utf-8")

def main(then_path: str, now_path: str, verbose: bool = True):
    """
    Compare two python paths and print the difference
    """
    if not now_path.endswith(".py"):
        return None, None, None
    with _open_utf(then_path) as f_then:
        then_ast = ast.parse(f_then.read())

    with _open_utf(now_path) as f_now:
        now_ast = ast.parse(f_now.read())

    _diff = DeepDiff(then_ast, now_ast, exclude_obj_callback=callback, iterable_compare_func=match_pairs)
    if _diff and verbose:
        print_diff(_diff, now_path, then_ast, now_ast)

    return now_ast, then_ast, _diff





if __name__ == "__main__":
    now, then, diff = main(sys.argv[1], sys.argv[2])
