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

class CompareConstants:
    def match(self, level):
        return isinstance(level.t1, ast.Constant) and isinstance(level.t2, ast.Constant)

    def give_up_diffing(self, level, diff_instance):
        if level.t1.value != level.t2.value:
            diff_instance._report_result('values_changed', level)

        return True


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

    # This also includes end_lineno and end_col_offset
    ignored_props = {"type_ignores", "type_comment", "col_offset", "lineno"}
    callback = lambda _, path: any(path.endswith(prop) for prop in ignored_props)
    compare_constants = CompareConstants()
    diff = DeepDiff(then_ast, now_ast, exclude_obj_callback=callback, custom_operators=[compare_constants])
    if diff and verbose:
        print_diff(diff, now_path, then_ast, now_ast)

    return now_ast, then_ast, diff





if __name__ == "__main__":
    now, then, diff = main(sys.argv[1], sys.argv[2])
