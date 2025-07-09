# This file contains codes for incremental updates as new transactions are added to the database
from fp_node import UtilityFPNode
from fp_tree_builder import _update_header_link


def incremental_fp_tree_update(transactions, fp_tree, header_table, original_sorted_items_order, min_util, external_utility=None):
    if external_utility is None:
        external_utility = {}
        for tx in transactions:
            for item_id, _, utility in tx:
                if item_id not in external_utility:
                    external_utility[item_id] = 0
                external_utility[item_id] += utility

    # identify items already in the current header table
    items_already_in_tree = set(header_table.keys())

    print(f"\n--- Second Pass: Inserting {(len(transactions))} new transactions___")

    for transaction in transactions:
        if not isinstance(transaction, list):
            print(f"Skipping invalid transaction: {transaction}")
            continue

        item_quantities = {item: quantity for item, quantity, _ in transaction}
        path_to_insert = [item for item in original_sorted_items_order if item in item_quantities and item in
                          items_already_in_tree]

        if not path_to_insert:
            print(f" Skipping transaction {transaction} - no existing header items or empty after filtering.")
            continue

        print(f" Processing transaction: {transaction}, Filtered/Sorted Path: {path_to_insert}")

        current_node_in_tree = fp_tree
        for item_on_path in path_to_insert:
            quantity_of_item = item_quantities[item_on_path]
            utility_of_one_unit = external_utility[item_on_path]
            # safe dictionary access
            item_utility_in_this_transaction = quantity_of_item * utility_of_one_unit
            child_node = current_node_in_tree.get_child(item_on_path)

            if child_node is None:
                new_node = UtilityFPNode(item_name=item_on_path, count=1, parent_node=current_node_in_tree)
                new_node.utility = item_utility_in_this_transaction
                current_node_in_tree.add_child(new_node)
                _update_header_link(item_on_path, new_node, header_table)
                print(f" Added new node for '{item_on_path}' with utility {item_utility_in_this_transaction}")
            else:
                child_node.count += 1
                child_node.utility += item_utility_in_this_transaction
                current_node_in_tree = child_node
                print(f" Updated existing node '{item_on_path}', new count {child_node.count}, new utility "
                      f"{child_node.utility}")

    # Calculate TWU for new items in transactions
    new_item_twu = {}
    all_items_in_new_transactions = set()
    transaction_utilities_new = []

    for transaction in transactions:
        trans_utility = 0
        current_transaction_items = set()
        for item, quantity, _ in transaction:
            current_transaction_items.add(item)
            trans_utility += quantity * external_utility.get(item, 0)
        transaction_utilities_new.append({'items': current_transaction_items.copy(), 'utility': trans_utility})
        all_items_in_new_transactions.update(current_transaction_items)

    potential_high_utility_items = all_items_in_new_transactions - items_already_in_tree
    print(f"Items appearing in new transactions not in original header: {potential_high_utility_items}")

    for item_candidate in potential_high_utility_items:
        twu = sum(trans_data['utility'] for trans_data in transaction_utilities_new if item_candidate in trans_data
                  ['items'])
        new_item_twu[item_candidate] = twu
        print(f" Calculated TWU for new item '{item_candidate}': {twu}")

    # Check the minimum utility of newly discovered items
    newly_discovered_high_utility_items = [
        item for item, twu_score in new_item_twu.items() if twu_score >= min_util
    ]
    if newly_discovered_high_utility_items:
        print("\n  WARNING: New items became high-potential. The current FP-Tree might be")
        print("  suboptimal or incomplete for these items without a more complex rebuild strategy.")
        print("  Consider a full tree rebuild if precise HUI mining with these new items is critical.")
        for item in newly_discovered_high_utility_items:
            print(f"    New item '{item}' (TWU: {new_item_twu[item]}) now meets min_util ({min_util})!")
            print(f"    ACTION NEEDED: Item '{item}' requires further processing (e.g., partial rebuild).")

    print("\nIncremental update finished")
    return fp_tree, header_table
