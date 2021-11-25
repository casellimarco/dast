from deepdiff.diff import (PASSES_COUNT, notpresent_indexed, SubscriptableIterableRelationship,
                           DeepDiff, OrderedSetPlus, notpresent, add_to_frozen_set)

class Diff(DeepDiff):
    mapping = {}

    def _diff_iterable_with_deephash(self, level, parents_ids, _original_type=None):
        """Diff of hashable or unhashable iterables. Only used when ignoring the order."""

        full_t1_hashtable = self._create_hashtable(level, 't1')
        full_t2_hashtable = self._create_hashtable(level, 't2')
        t1_hashes = OrderedSetPlus(full_t1_hashtable.keys())
        t2_hashes = OrderedSetPlus(full_t2_hashtable.keys())
        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        # Deciding whether to calculate pairs or not.
        if (len(hashes_added) + len(hashes_removed)) / (len(full_t1_hashtable) + len(full_t2_hashtable) + 1) > self.cutoff_intersection_for_pairs:
            get_pairs = False
        else:
            get_pairs = True

        # reduce the size of hashtables
        if self.report_repetition:
            t1_hashtable = full_t1_hashtable
            t2_hashtable = full_t2_hashtable
        else:
            t1_hashtable = {k: v for k, v in full_t1_hashtable.items() if k in hashes_removed}
            t2_hashtable = {k: v for k, v in full_t2_hashtable.items() if k in hashes_added}

        if self._stats[PASSES_COUNT] < self.max_passes and get_pairs:
            self._stats[PASSES_COUNT] += 1
            pairs = self._get_most_in_common_pairs_in_iterables(
                hashes_added, hashes_removed, t1_hashtable, t2_hashtable, parents_ids, _original_type)
        elif get_pairs:
            if not self._stats[MAX_PASS_LIMIT_REACHED]:
                self._stats[MAX_PASS_LIMIT_REACHED] = True
                logger.warning(MAX_PASSES_REACHED_MSG.format(self.max_passes))
            pairs = dict_()
        else:
            pairs = dict_()

        # Added block
        mapping = []
        for maybe_t1_hash, maybe_t2_hash in pairs.items():
            if maybe_t1_hash in t1_hashes:
                t1_index = t1_hashes.index(maybe_t1_hash)
                t2_index = t2_hashes.index(maybe_t2_hash)
                if t1_index != t2_index:
                    mapping.append((t1_index, t2_index))
        for common_hash in t1_hashes & t2_hashes:
            t1_index = t1_hashes.index(common_hash)
            t2_index = t2_hashes.index(common_hash)
            if t1_index != t2_index:
                mapping.append((t1_index, t2_index))

        if mapping:
            self.mapping[level] = mapping

        def get_other_pair(hash_value, in_t1=True):
            """
            Gets the other paired indexed hash item to the hash_value in the pairs dictionary
            in_t1: are we looking for the other pair in t1 or t2?
            """
            if in_t1:
                hashtable = t1_hashtable
                the_other_hashes = hashes_removed
            else:
                hashtable = t2_hashtable
                the_other_hashes = hashes_added
            other = pairs.pop(hash_value, notpresent)
            if other is notpresent:
                other = notpresent_indexed
            else:
                # The pairs are symmetrical.
                # removing the other direction of pair
                # so it does not get used.
                del pairs[other]
                the_other_hashes.remove(other)
                other = hashtable[other]
            return other

        if self.report_repetition:
            for hash_value in hashes_added:
                if self._count_diff() is StopIteration:
                    return  # pragma: no cover. This is already covered for addition (when report_repetition=False).
                other = get_other_pair(hash_value)
                item_id = id(other.item)
                indexes = t2_hashtable[hash_value].indexes if other.item is notpresent else other.indexes
                for i in indexes:
                    change_level = level.branch_deeper(
                        other.item,
                        t2_hashtable[hash_value].item,
                        child_relationship_class=SubscriptableIterableRelationship,
                        child_relationship_param=i
                    )
                    if other.item is notpresent:
                        self._report_result('iterable_item_added', change_level)
                    else:
                        parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                        self._diff(change_level, parents_ids_added)
            for hash_value in hashes_removed:
                if self._count_diff() is StopIteration:
                    return  # pragma: no cover. This is already covered for addition.
                other = get_other_pair(hash_value, in_t1=False)
                item_id = id(other.item)
                for i in t1_hashtable[hash_value].indexes:
                    change_level = level.branch_deeper(
                        t1_hashtable[hash_value].item,
                        other.item,
                        child_relationship_class=SubscriptableIterableRelationship,
                        child_relationship_param=i)
                    if other.item is notpresent:
                        self._report_result('iterable_item_removed', change_level)
                    else:
                        # I was not able to make a test case for the following 2 lines since the cases end up
                        # getting resolved above in the hashes_added calcs. However I am leaving these 2 lines
                        # in case things change in future.
                        parents_ids_added = add_to_frozen_set(parents_ids, item_id)  # pragma: no cover.
                        self._diff(change_level, parents_ids_added)  # pragma: no cover.

            items_intersect = t2_hashes.intersection(t1_hashes)

            for hash_value in items_intersect:
                t1_indexes = t1_hashtable[hash_value].indexes
                t2_indexes = t2_hashtable[hash_value].indexes
                t1_indexes_len = len(t1_indexes)
                t2_indexes_len = len(t2_indexes)
                if t1_indexes_len != t2_indexes_len:  # this is a repetition change!
                    # create "change" entry, keep current level untouched to handle further changes
                    repetition_change_level = level.branch_deeper(
                        t1_hashtable[hash_value].item,
                        t2_hashtable[hash_value].item,  # nb: those are equal!
                        child_relationship_class=SubscriptableIterableRelationship,
                        child_relationship_param=t1_hashtable[hash_value]
                        .indexes[0])
                    repetition_change_level.additional['repetition'] = RemapDict(
                        old_repeat=t1_indexes_len,
                        new_repeat=t2_indexes_len,
                        old_indexes=t1_indexes,
                        new_indexes=t2_indexes)
                    self._report_result('repetition_change',
                                         repetition_change_level)

        else:
            for hash_value in hashes_added:
                if self._count_diff() is StopIteration:
                    return
                other = get_other_pair(hash_value)
                item_id = id(other.item)
                index = t2_hashtable[hash_value].indexes[0] if other.item is notpresent else other.indexes[0]
                change_level = level.branch_deeper(
                    other.item,
                    t2_hashtable[hash_value].item,
                    child_relationship_class=SubscriptableIterableRelationship,
                    child_relationship_param=index)
                if other.item is notpresent:
                    self._report_result('iterable_item_added', change_level)
                else:
                    parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                    self._diff(change_level, parents_ids_added)

            for hash_value in hashes_removed:
                if self._count_diff() is StopIteration:
                    return  # pragma: no cover. This is already covered for addition.
                other = get_other_pair(hash_value, in_t1=False)
                item_id = id(other.item)
                change_level = level.branch_deeper(
                    t1_hashtable[hash_value].item,
                    other.item,
                    child_relationship_class=SubscriptableIterableRelationship,
                    child_relationship_param=t1_hashtable[hash_value].indexes[
                        0])
                if other.item is notpresent:
                    self._report_result('iterable_item_removed', change_level)
                else:
                    # Just like the case when report_repetition = True, these lines never run currently.
                    # However they will stay here in case things change in future.
                    parents_ids_added = add_to_frozen_set(parents_ids, item_id)  # pragma: no cover.
                    self._diff(change_level, parents_ids_added)  # pragma: no cover.

