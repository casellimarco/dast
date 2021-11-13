import sys
import ast
from deepdiff import DeepDiff

from dast.from_ast import strip
from dast import pprint_ast as _ # Side-effects only

def main(then_path, now_path):
    with open(sys.argv[1]) as f:
        then = ast.parse(f.read())
        strip(then)

    with open(sys.argv[2]) as f:
        now = ast.parse(f.read())
        strip(now)

    diff = DeepDiff(then, now)
    if diff:
        print(diff)

    return now, then

if __name__ == "__main__":
    now, then = main(sys.argv[1], sys.argv[2])