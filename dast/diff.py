"""
This script contains only modifications to deepdiff core classes.
The edits are clearly highlighted through comments, anything else is just copy pasted from source
"""


from deepdiff.diff import (PASSES_COUNT, notpresent_indexed, SubscriptableIterableRelationship,
                           DeepDiff, OrderedSetPlus, notpresent, add_to_frozen_set)

from deepdiff.deephash import (DeepHash, EMPTY_FROZENSET, dict_, logger, get_id, KEY_TO_VAL_STR, unprocessed)

class Hash(DeepHash):
    def _prep_iterable(self, obj, parent, parents_ids=EMPTY_FROZENSET):

        counts = 1
# --- begin diff wrt to deepdiff ---
        result = set()
# --- end diff wrt to deepdiff ---

        for i, item in enumerate(obj):
            new_parent = "{}[{}]".format(parent, i)
            if self._skip_this(item, parent=new_parent):
                continue

            item_id = get_id(item)
            if parents_ids and item_id in parents_ids:
                continue

            parents_ids_added = add_to_frozen_set(parents_ids, item_id)
            hashed, count = self._hash(item, parent=new_parent, parents_ids=parents_ids_added)
            # counting repetitions
            counts += count
# --- begin diff wrt to deepdiff ---
            result.add((hashed, i))

        if self.ignore_repetition:
            result = list(set(map(lambda x: x[0], result)))
        else:
            result = [
                f'{hashed}|{i}' for hashed, i in result
            ]
# --- end diff wrt to deepdiff ---

        result = sorted(map(str, result))  # making sure the result items are string and sorted so join command works.
        result = ','.join(result)
        result = KEY_TO_VAL_STR.format(type(obj).__name__, result)

        return result, counts

class Diff(DeepDiff):
    mapping = {}

    def _get_matching_pairs(self, level):
        """
        Given a level get matching pairs. This returns list of two tuples in the form:
        [
          (t1 index, t2 index), (t1 item, t2 item)
        ]

        This will compare using the passed in `iterable_compare_func` if available.
        Default it to compare in order
        """

        if(self.iterable_compare_func is None):
            # Match in order if there is no compare function provided
            return self._compare_in_order(level)
        try:
            matches = []
            y_matched = set()
            y_index_matched = set()
            for i, x in enumerate(level.t1):
                x_found = False
                for j, y in enumerate(level.t2):

                    if(j in y_index_matched):
                        # This ensures a one-to-one relationship of matches from t1 to t2.
                        # If y this index in t2 has already been matched to another x
                        # it cannot have another match, so just continue.
                        continue

                    if(self.iterable_compare_func(x, y, level)):
# --- begin diff wrt to deepdiff ---
                        deep_hash = Hash(y,
# --- end diff wrt to deepdiff ---
                                             hashes=self.hashes,
                                             apply_hash=True,
                                             **self.deephash_parameters,
                                             )
                        y_index_matched.add(j)
                        y_matched.add(deep_hash[y])
                        matches.append(((i, j), (x, y)))
                        x_found = True
                        break

                if(not x_found):
                    matches.append(((i, -1), (x, ListItemRemovedOrAdded)))
            for j, y in enumerate(level.t2):

# --- begin diff wrt to deepdiff ---
                deep_hash = Hash(y,
# --- end diff wrt to deepdiff ---
                                     hashes=self.hashes,
                                     apply_hash=True,
                                     **self.deephash_parameters,
                                     )
                if(deep_hash[y] not in y_matched):
                    matches.append(((-1, j), (ListItemRemovedOrAdded, y)))
            return matches
        except CannotCompare:
            return self._compare_in_order(level)

    def _create_hashtable(self, level, t):
        """Create hashtable of {item_hash: (indexes, item)}"""
        obj = getattr(level, t)

        local_hashes = dict_()
        for (i, item) in enumerate(obj):
            try:
                parent = "{}[{}]".format(level.path(), i)
                # Note: in the DeepDiff we only calculate the hash of items when we have to.
                # So self.hashes does not include hashes of all objects in t1 and t2.
                # It only includes the ones needed when comparing iterables.
                # The self.hashes dictionary gets shared between different runs of DeepHash
                # So that any object that is already calculated to have a hash is not re-calculated.
# --- begin diff wrt to deepdiff ---
                deep_hash = Hash(item,
# --- end diff wrt to deepdiff ---
                                     hashes=self.hashes,
                                     parent=parent,
                                     apply_hash=True,
                                     **self.deephash_parameters,
                                     )
                item_hash = deep_hash[item]
            except Exception as e:  # pragma: no cover
                logger.error("Can not produce a hash for %s."
                             "Not counting this object.\n %s" %
                             (level.path(), e))
            else:
                if item_hash is unprocessed:  # pragma: no cover
                    logger.warning("Item %s was not processed while hashing "
                                   "thus not counting this object." %
                                   level.path())
                else:
                    self._add_hash(hashes=local_hashes, item_hash=item_hash, item=item, i=i)

        # Also we hash the iterables themselves too so that we can later create cache keys from those hashes.
        try:
# --- begin diff wrt to deepdiff ---
            Hash(
# --- end diff wrt to deepdiff ---
                obj,
                hashes=self.hashes,
                parent=level.path(),
                apply_hash=True,
                **self.deephash_parameters,
            )
        except Exception as e:  # pragma: no cover
            logger.error("Can not produce a hash for iterable %s. %s" %
                         (level.path(), e))
        return local_hashes

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

# --- begin diff wrt to deepdiff ---
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
# --- end diff wrt to deepdiff ---

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

