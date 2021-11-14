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

from dast.from_ast import strip, prettify

_open_utf = partial(open, encoding="utf-8")

def main(then_path: str, now_path: str, verbose: bool = True):
    """
    Compare two python paths and print the difference
    """
    if not now_path.endswith(".py"):
        return None, None
    with _open_utf(then_path) as f_then:
        then_ast = ast.parse(f_then.read())
        strip(then_ast)
        prettify(then_ast)

    with _open_utf(now_path) as f_now:
        now_ast = ast.parse(f_now.read())
        strip(now_ast)
        prettify(now_ast)

    diff = Diff(then_ast, now_ast)
    if diff and verbose:
        print(f"diff for file {now_path}")
        print(diff)

    return now_ast, then_ast

if __name__ == "__main__":
    now, then = main(sys.argv[1], sys.argv[2])
