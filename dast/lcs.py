"""
Longest Common Subsequence problem
"""
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple

def get_lcs(xs: Iterable[Any], ys: Iterable[Any]):
    """
    Longest common subsequence between two finite iterables via dynamic programming.

    >>> get_lcs("abcde", "abfgdfe")
    ['a', 'b', 'd', 'e']
    """
    # sub_problems[i, j] = LCS between all_x[:i] and all_y[:j]
    sub_problems: Dict[Tuple[int, int], List] = defaultdict(list)

    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if x == y:
                sub_problems[i + 1, j + 1] = sub_problems[i, j] + [x]
            else:
                sub_problems[i + 1, j + 1] = max(
                    sub_problems[i, j + 1],
                    sub_problems[i + 1, j],
                    key=len)

    return sub_problems[len(list(xs)), len(list(ys))]
