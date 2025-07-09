# this class file contains code for pruning the search space.
def construct_pruned_item_list(transactions, min_util, external_utility=None):
    """
    Prune items with low utility. If external_utility is None, build it from transactions using the real utility values.
    """
    if external_utility is None:
        # Build external_utility from transactions
        external_utility = {}
        for tx in transactions:
            for item_id, _, utility in tx:
                if item_id not in external_utility:
                    external_utility[item_id] = 0
                external_utility[item_id] += utility

    if not isinstance(external_utility, dict):
        raise ValueError("external_utility must be a dictionary")

    # Prune items below min_util
    pruned_items = [item for item, util in external_utility.items() if util >= min_util]
    # Sort by utility descending
    pruned_items.sort(key=lambda x: external_utility[x], reverse=True)
    return pruned_items



