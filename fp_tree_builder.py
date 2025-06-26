# This codes will construct the FP-Tree for the HUIM
from fp_node import UtilityFPNode


def construct_huim_fp_tree(transaction_database, sorted_items, external_utility):
    # Initialize a root variable to store the class UtilityFPNode
    # And a header table

    # Input Validation
    if not isinstance(transaction_database, list):
        raise ValueError("transaction_database must be a list")
    if not isinstance(sorted_items, list):
        raise ValueError("sorted_items must be a list")
    if not isinstance(external_utility, dict):
        raise ValueError("external_utility must be a dictionary")

    # initialize root and header table
    root = UtilityFPNode(None, 0, None)
    header_table = {}

    # process each transaction
    for transaction in transaction_database:
        if not isinstance(transaction, list):
            raise ValueError("Each transaction must be a list of (item, quantity) tuples")
        # get item quantities
        item_quantities = {item: quantity for item, quantity in transaction}

        # filter and sort items by twu order
        trans_sorted_items = [item for item in sorted_items if item in item_quantities]

        # skip empty transactions
        if not trans_sorted_items:
            continue

        # build path in the tree
        current_node = root
        for item in trans_sorted_items:
            quantity_of_item = item_quantities[item]
            if item not in external_utility:
                raise ValueError(f"Item {item} is not found in external_utility")
            utility_of_one_item = external_utility[item]
            item_utility_in_transaction = quantity_of_item * utility_of_one_item

            # check for existing child
            child = current_node.get_child(item)
            if child is None:
                # create new node
                child = UtilityFPNode(item_name=item, count=1, parent_node=current_node)
                child.utility = item_utility_in_transaction
                current_node.add_child(child)
                _update_header_link(item, child, header_table)
            else:
                # update existing node
                child.count = 1
                child.utility += item_utility_in_transaction
                current_node = child

        return root, header_table


# a function to update the header link
def _update_header_link(item_name, new_node_for_item, header_table):
    # if item is new to the header table, it becomes the head of the list
    if item_name not in header_table:
        header_table[item_name] = new_node_for_item
    else:
        current_linked_node = header_table[item_name]
        # find the last node in the chain
        while current_linked_node.node_link is not None:
            current_linked_node = current_linked_node.node_link

        if current_linked_node != new_node_for_item:
            current_linked_node.node_link = new_node_for_item
