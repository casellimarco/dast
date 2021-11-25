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

from dast.diff import Diff

from dast.from_ast import prettify

_open_utf = partial(open, encoding="utf-8")

def main(then_path: str, now_path: str, verbose: bool = True):
    """
    Compare two python paths and print the difference
    """
    if not now_path.endswith(".py"):
        return None, None
    with _open_utf(then_path) as f_then:
        then_ast = ast.parse(f_then.read())
        prettify(then_ast)

    with _open_utf(now_path) as f_now:
        now_ast = ast.parse(f_now.read())
        prettify(now_ast)

    # This also includes end_lineno and end_col_offset
    ignored_props = {"type_ignores", "type_comment", "col_offset", "lineno"}
    callback = lambda _, path: any(path.endswith(prop) for prop in ignored_props)
    diff = Diff(then_ast, now_ast, exclude_obj_callback=callback)
    if diff and verbose:
        print(f"diff for file {now_path}")
        print(diff)

    return now_ast, then_ast

if __name__ == "__main__":
    now, then = main(sys.argv[1], sys.argv[2])
