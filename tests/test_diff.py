import pytest
from dast.diff import Diff

def test_mapping():
    t1 = [[1, 2, 3], [4, 5]]
    t2 = [[4, 5, 6], [1, 2, 3]]
    ddiff = Diff(t1, t2, ignore_order=True)
    assert len(ddiff.mapping) == 1
    assert list(ddiff.mapping.values())[0] == [(1,0),(0,1)]
    assert {'iterable_item_added': {'root[1][2]': 6}} == ddiff

def test_mapping_deeper():
    t1 = [[[1, 2, 3]]]
    t2 = [[[3, 2, 1]]]
    ddiff = Diff(t1, t2, ignore_order=True)
    # this test fails due to t1 and t2 getting the same hash from DeepHash._prep_iterable()
    # assert len(ddiff.mapping) == 1
    # assert list(ddiff.mapping.values())[0] == [(2,0),(0,2)]
    assert {} == ddiff

def test_mapping_deeper_tuples():
    t1 = [((1, 2, 3),)]
    t2 = [((3, 2, 1),)]
    ddiff = Diff(t1, t2, ignore_order=True)
    # normal tuples are process as iterables....
    # assert len(ddiff.mapping) == 1
    # assert list(ddiff.mapping.values())[0] == [(2,0),(0,2)]
    assert {} == ddiff
