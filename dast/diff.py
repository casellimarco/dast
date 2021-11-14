"""
The main logic for the diff as it differs from DeepDiff
"""
from deepdiff import DeepDiff, DeepHash
from deepdiff.diff import ListItemRemovedOrAdded, DiffLevel

from dast.lcs import get_lcs

class Diff(DeepDiff):
    def _get_matching_pairs(self, level):
        """
        Given a level get matching pairs. This returns list of two tuples in the form:
        [
          (t1 index, t2 index), (t1 item, t2 item)
        ]

        Will compute the LCS between the two levels by using the DistanceMixin and a maximum cutoff threshold
        """
        t1_hashes = DeepHash(level.t1)
        t1 = [t1_hashes[obj] for obj in level.t1]
        t2_hashes = DeepHash(level.t2)
        t2 = [t2_hashes[obj] for obj in level.t2]

        lcs = get_lcs(t1, t2)

        pairs = []

        i = 0
        j = 0
        n = 0
        while any([n < len(lcs), i < len(t1), j < len(t2)]):
            try:
                if t1[i] == t2[j] == lcs[n]:
                    pairs.append((
                        (i, j), (level.t1[i], level.t2[j])
                    ))
                    i += 1
                    j += 1
                    n += 1
            except IndexError:
                pass
            try:
                if t1[i] != lcs[n]:
                    pairs.append((
                        (i, -1), (level.t1[i], ListItemRemovedOrAdded)
                    ))
                    i += 1
            except IndexError:
                pass
            try:
                if t2[j] != lcs[n]:
                    pairs.append((
                        (-1, j), (ListItemRemovedOrAdded, level.t2[j])
                    ))
                    j += 1
            except IndexError:
                pass
        return pairs
