"""
Longest Common Subsequence problem
"""
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple

def get_lcs(xs: Iterable[Any], ys: Iterable[Any]):
    """
    Longest common subsequence between two finite iterables via dynamic programming.

    >>> get_lcs("abcde", "abfgdfe")
    (['a', 'b', 'd', 'e'], [True, True, False, True, True], [True, True, False, False, True, False, True])
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

    lcs = sub_problems[len(list(xs)), len(list(ys))]

    return lcs, sequence_in_lcs(xs, lcs), sequence_in_lcs(ys, lcs)

def sequence_in_lcs(xs: Iterable, lcs: List) -> List[bool]:
    """
    Determine which characters from a sequence are in another

    >>> sequence_in_lcs("abcde", ["a","c"])
    [True, False, True, False, False]
    >>> sequence_in_lcs("a", ["a","c"])
    [True]
    """
    x_in_lcs = []
    n = 0
    for x in xs:
        if len(lcs) > n and x == lcs[n]:
            x_in_lcs.append(True)
            n += 1
        else:
            x_in_lcs.append(False)

    return x_in_lcs
