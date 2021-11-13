"""
Longest Common Subsequence problem
"""
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple

def get_lcs(x: Iterable[Any], y: Iterable[Any]):
    """
    Longest common subsequence between two finite iterables via dynamic programming.

    >>> get_lcs("abcde", "abfgdfe")
    (['a', 'b', 'd', 'e'], [True, True, False, True, True], [True, True, False, False, True, False, True])
    """
    all_x = list(x)
    all_y = list(y)
    num_x = len(all_x)
    num_y = len(all_y)

    # sub_problems[i, j] = LCS between all_x[:i] and all_y[:j]
    sub_problems: Dict[Tuple[int, int], List] = defaultdict(list)

    for i in range(num_x):
        for j in range(num_y):
            if all_x[i] == all_y[j]:
                sub_problems[i + 1, j + 1] = sub_problems[i, j] + [all_x[i]]
            else:
                sub_problems[i + 1, j + 1] = max(
                    sub_problems[i, j + 1],
                    sub_problems[i + 1, j],
                    key=len)

    lcs = sub_problems[num_x, num_y]

    return lcs, sequence_in_lcs(all_x, lcs), sequence_in_lcs(all_y, lcs)

def sequence_in_lcs(x: Iterable, lcs: List) -> List[bool]:
    """
    Determine which characters from a sequence are in another
    """
    x_in_lcs = []
    n = 0
    for element in x:
        if element == lcs[n]:
            x_in_lcs.append(True)
            n += 1
        else:
            x_in_lcs.append(False)

    return x_in_lcs
