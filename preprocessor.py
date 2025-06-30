# this class file contains code for pruning the search space.
def construct_pruned_item_list(transaction_database, min_util, external_utility):

    # Input validation
    if not isinstance(transaction_database, list):
        raise ValueError("transaction_database must be a list.")
    if not isinstance(min_util, (int, float)) or min_util < 0:
        raise ValueError("min_util must be a non-negative number")
    if not isinstance(external_utility, dict):
        raise ValueError("external_utility must be a dictionary")
    # define the variable for the Transactional Weighted Utility of an item
    item_twu = {}

    # the utility of an item is the quantity * external utility
    # the transaction utility is the sum of the individual item utilities in a transaction
    for transaction in transaction_database:
        if not isinstance(transaction, list):
            raise ValueError("Each transaction must be list of item (item, quantity) tuples")
        transaction_utility = 0
        for item, quantity in transaction:
            if item not in external_utility:
                raise ValueError(f"item {item} is not found in external utility")
            if not isinstance(quantity, (int,float)) or quantity < 0:
                raise ValueError(f"Quantity for item {item} must be non-negative")
            transaction_utility += quantity * external_utility[item]

        # Update TWU for each item in the transaction
        for item, _ in transaction:
            item_twu[item] = item_twu.get(item, 0) + transaction_utility

    # filter high utility items
    high_utility_items = {item for item, twu in item_twu.items() if twu >= min_util}

    # sort high-utility items by TWU in descending order
    sorted_items = sorted(high_utility_items, key=lambda item: item_twu[item], reverse=True)

    return sorted_items



